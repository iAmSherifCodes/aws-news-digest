const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, ScanCommand } = require('@aws-sdk/lib-dynamodb');
const { SNSClient, PublishCommand } = require('@aws-sdk/client-sns');
const sendEmail = require('./mail_setup').sendEmail;

const client = new DynamoDBClient({ region: 'us-east-1' });
const dynamodb = DynamoDBDocumentClient.from(client);
const sns = new SNSClient({ region: 'us-east-1' });

const POSTS_TABLE = process.env.POSTS_TABLE;
const USERS_TABLE = process.env.USERS_TABLE;
const FROM_EMAIL = process.env.FROM_EMAIL;
const SNS_TOPIC_ARN = process.env.SNS_TOPIC_ARN;

async function getPostsByDate(date) {
    try {
        const response = await dynamodb.send(new ScanCommand({
            TableName: POSTS_TABLE,
            FilterExpression: 'begins_with(#date, :date_val)',
            ExpressionAttributeNames: {
                '#date': 'date'
            },
            ExpressionAttributeValues: {
                ':date_val': date
            }
        }));
        return response.Items || [];
    } catch (error) {
        console.error(`Error retrieving post(s): ${error.message}`);
        throw error;
    }
}

async function getSubscribedUsers(categories) {
    try {
        const response = await dynamodb.send(new ScanCommand({
            TableName: USERS_TABLE
        }));
        
        const users = response.Items || [];
        console.log('Users:', users);
        
        // Extract category names from category objects
        const categoryNames = categories.map(cat => cat.categories || []).flat();
        // console.log('CategoriesNames:', categoryNames);

        const subscribedUsers = users.filter(user => {
            const userCategories = user.categories || [];
            return categoryNames.some(category => userCategories.includes(category));
        });

        
        return subscribedUsers;
    } catch (error) {
        console.error(`Error getting subscribed users: ${error.message}`);
        throw error;
    }
}

async function getCategoriesByDate(date) {
    const CATEGORIES_TABLE = process.env.CATEGORIES_TABLE || 'suo-categories';
    try {
        const response = await dynamodb.send(new ScanCommand({
            TableName: CATEGORIES_TABLE,
            FilterExpression: '#date = :date_val',
            ExpressionAttributeNames: {
                '#date': 'date'
            },
            ExpressionAttributeValues: {
                ':date_val': date
            }
        }));
        return response.Items || [];
    } catch (error) {
        console.error(`Error fetching categories: ${error.message}`);
        throw error;
    }
}

async function sendErrorNotification(error, context = {}) {
    if (!SNS_TOPIC_ARN) {
        console.warn('SNS_TOPIC_ARN not configured, skipping error notification');
        return;
    }
    
    try {
        const message = {
            error: error.message,
            stack: error.stack,
            timestamp: new Date().toISOString(),
            ...context
        };
        
        await sns.send(new PublishCommand({
            TopicArn: SNS_TOPIC_ARN,
            Subject: 'SUO-AWS Notifier Error',
            Message: JSON.stringify(message, null, 2)
        }));
        
        console.log('Error notification sent via SNS');
    } catch (snsError) {
        console.error('Failed to send SNS notification:', snsError.message);
    }
}

async function sendCategorizedNewsToSubscribers(posts, subscribers) {
  const newsByCategory = {};
  for (const news of posts) {
    const category = news.category.toLowerCase();
    if (!newsByCategory[category]) {
      newsByCategory[category] = [];
    }
    newsByCategory[category].push(news);
  }

    // Go through each subscriber
    for (const subscriber of subscribers) {
        if (!subscriber.active) continue;
    
        const matchedNews = [];
    
        for (const category of subscriber.categories) {
          const lowerCategory = category.toLowerCase();
          if (newsByCategory[lowerCategory]) {
            matchedNews.push(...newsByCategory[lowerCategory]);
          }
        }
    
        if (matchedNews.length > 0) {
            console.log(`Sending news to ${subscriber.name} (${subscriber.email}) for categories: ${subscriber.categories.join(', ')}`);

        const text = matchedNews.map(news =>
          `• ${news.title}\n${news.description}\n`
        ).join('\n');

        const subject = `SUO-AWS Daily News: ${matchedNews[0].date}`;
        const html = matchedNews.map(news =>
            `<li><strong>${news.title}</strong><br>${news.description}<br><a href="${news.url}">Read more</a></li>`
        ).join('');
        
        await sendEmail('SUO AWS NEWS', FROM_EMAIL, subscriber.name, subscriber.email, subject, text, html)
        }
    }
}

function getPreviousDate() {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    
    const mm = String(yesterday.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
    const dd = String(yesterday.getDate()).padStart(2, '0');
    const yyyy = yesterday.getFullYear();
  
    return `${mm}/${dd}/${yyyy}`;
}
  
  
exports.handler = async (event, context) => {
    console.log('Starting notification process');
    
    try {
        // check if target_date is in event if not use getPreviousDate
        let date = JSON.parse(event.body.target_date);
        if (!date) {
            date = getPreviousDate();
        }
        console.log('Fetching posts for date:', date);
        
        const posts = await getPostsByDate(date); 
        console.log('Posts:', posts.length);      
        if (!posts || posts.length === 0) {
            return {
                statusCode: 404,
                body: JSON.stringify({ message: `No posts found for date ${date}` })
            };
        }

        const categories = await getCategoriesByDate(date);
        // console.log('Categories:', categories);

        const subscribedUsers = await getSubscribedUsers(categories);
        // console.log('Subscribed users:', subscribedUsers.length);

        await sendCategorizedNewsToSubscribers(posts, subscribedUsers);
        // console.log('Notifications sent to all subscribed users');
        
        return {
            statusCode: 200,
            body: JSON.stringify({
                message: `Found ${posts.length} posts and ${subscribedUsers.length} subscribed users`,
                date: date
            })
        };
    } catch (error) {
        console.error(`Error in handler: ${error.message}`);
        await sendErrorNotification(error, { event, functionName: 'notifier' });
        return {
            statusCode: 500,
            body: JSON.stringify({ message: `Error sending notifications: ${error.message}` })
        };
    }
};

// For local testing
// if (require.main === module) {
//     const testEvent = {
//         post_id: '670729a3-71dd-4519-8719-ee201a1812b2'
//     };
//     exports.handler(testEvent, null).then(console.log);
// }
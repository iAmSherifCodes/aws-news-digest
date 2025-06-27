const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, PutCommand, ScanCommand } = require('@aws-sdk/lib-dynamodb');

const client = new DynamoDBClient({ region: process.env.AWS_REGION });
const dynamodb = DynamoDBDocumentClient.from(client);

const USERS_TABLE = process.env.USERS_TABLE;

function validateInput(event) {
    const { name, email, categories } = event;
    
    if (!name || typeof name !== 'string' || name.trim().length === 0) {
        throw new Error('Name is required and must be a non-empty string');
    }
    
    if (!email || typeof email !== 'string' || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        throw new Error('Valid email is required');
    }
    
    if (!categories || !Array.isArray(categories) || categories.length === 0) {
        throw new Error('Categories must be a non-empty array');
    }
    
    return { name: name.trim(), email: email.trim(), categories };
}

exports.handler = async (event) => {
    try {
        const { name, email, categories } = validateInput(event);
        
        const existingUser = await dynamodb.send(new ScanCommand({
            TableName: USERS_TABLE,
            FilterExpression: 'email = :email',
            ExpressionAttributeValues: { ':email': email }
        }));
        
        if (existingUser.Items && existingUser.Items.length > 0) {
            throw new Error('User with this email already exists');
        }
        
        const item = {
            id: Date.now().toString(),
            email,
            name,
            categories,
            active: true,
            createdAt: new Date().toISOString()
        };
        
        await dynamodb.send(new PutCommand({
            TableName: USERS_TABLE,
            Item: item
        }));
        
        return {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Subscription created successfully',
                user: { name, email, categories }
            })
        };
    } catch (error) {
        console.error('Error creating subscription:', error.message);
        return {
            statusCode: 400,
            body: JSON.stringify({ error: error.message })
        };
    }
};
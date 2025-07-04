const { DynamoDBClient } = require('@aws-sdk/client-dynamodb');
const { DynamoDBDocumentClient, PutCommand, ScanCommand } = require('@aws-sdk/lib-dynamodb');
const { SESClient, SendEmailCommand } = require('@aws-sdk/client-ses');

const client = new DynamoDBClient({ region: process.env.AWS_REGION });
const dynamodb = DynamoDBDocumentClient.from(client);
const sesClient = new SESClient({ region: process.env.AWS_REGION });

const USERS_TABLE = process.env.USERS_TABLE;
const FROM_EMAIL = process.env.FROM_EMAIL || 'noreply@suo-aws.com';

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

async function sendWelcomeEmail(name, email, categories) {
    const categoriesList = categories.map(cat => `<div style="margin-bottom: 8px;"><span style="display: inline-block; background-color: #FF9900; color: #ffffff; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; margin-right: 8px;">${cat}</span></div>`).join('');
    
    const htmlTemplate = `<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="x-apple-disable-message-reformatting">
    <title>Welcome to SUO-AWS!</title>
    
    <style>
        /* Reset styles */
        body, table, td, a { -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }
        table, td { mso-table-lspace: 0pt; mso-table-rspace: 0pt; }
        img { -ms-interpolation-mode: bicubic; }

        /* Remove default styling */
        img { border: 0; height: auto; line-height: 100%; outline: none; text-decoration: none; }
        table { border-collapse: collapse !important; }
        body { height: 100% !important; margin: 0 !important; padding: 0 !important; width: 100% !important; }

        /* iOS BLUE LINKS */
        a[x-apple-data-detectors] {
            color: inherit !important;
            text-decoration: none !important;
            font-size: inherit !important;
            font-family: inherit !important;
            font-weight: inherit !important;
            line-height: inherit !important;
        }

        /* MOBILE STYLES */
        @media screen and (max-width: 600px) {
            .mobile-hide { display: none !important; }
            .mobile-center { text-align: center !important; }
            .mobile-padding { padding: 20px !important; }
        }

        /* DARK MODE STYLES */
        @media (prefers-color-scheme: dark) {
            .dark-mode-bg { background-color: #1a1a1a !important; }
            .dark-mode-text { color: #ffffff !important; }
            .dark-mode-card { background-color: #2a2a2a !important; }
            .dark-mode-border { border-color: #404040 !important; }
        }
    </style>
</head>

<body style="background-color: #f5f5f5; margin: 0 !important; padding: 0 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    
    <!-- HIDDEN PREHEADER TEXT -->
    <div style="display: none; font-size: 1px; color: #fefefe; line-height: 1px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-height: 0px; max-width: 0px; opacity: 0; overflow: hidden;">
        Welcome to SUO-AWS! Your subscription is confirmed and you'll start receiving AWS updates soon.
    </div>

    <table border="0" cellpadding="0" cellspacing="0" width="100%" class="dark-mode-bg">
        <!-- HEADER -->
        <tr>
            <td bgcolor="#FF9900" align="center" style="padding: 0px 10px 0px 10px;">
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                    <tr>
                        <td bgcolor="#FF9900" align="center" valign="top" style="padding: 40px 20px 40px 20px;">
                            <h1 style="font-size: 36px; font-weight: bold; margin: 0; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                                🎉 Welcome to SUO-AWS!
                            </h1>
                            <p style="font-size: 18px; margin: 10px 0 0 0; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                                Stay Updated On AWS
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>

        <!-- MAIN CONTENT -->
        <tr>
            <td bgcolor="#f5f5f5" align="center" style="padding: 0px 10px 0px 10px;" class="dark-mode-bg">
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                    <tr>
                        <td bgcolor="#ffffff" align="left" style="padding: 40px 40px 40px 40px; border-radius: 8px; border: 1px solid #e5e5e5;" class="mobile-padding dark-mode-card dark-mode-border">
                            
                            <h2 style="margin: 0 0 20px 0; font-size: 24px; font-weight: 600; color: #333333; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;" class="dark-mode-text">
                                Hi ${name}! 👋
                            </h2>
                            
                            <p style="margin: 0 0 20px 0; font-size: 16px; line-height: 24px; color: #333333; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;" class="dark-mode-text">
                                Thank you for subscribing to SUO-AWS! We're excited to help you stay updated on the latest AWS news and announcements.
                            </p>

                            <p style="margin: 0 0 30px 0; font-size: 16px; line-height: 24px; color: #333333; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;" class="dark-mode-text">
                                You've subscribed to receive updates for the following categories:
                            </p>

                            <!-- SUBSCRIBED CATEGORIES -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 20px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #FF9900;" class="dark-mode-card">
                                        <h3 style="margin: 0 0 15px 0; font-size: 18px; font-weight: 600; color: #FF9900; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
                                            Your Subscribed Categories
                                        </h3>
                                        <div style="font-size: 14px; line-height: 22px; color: #333333; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;" class="dark-mode-text">
                                            ${categoriesList}
                                        </div>
                                    </td>
                                </tr>
                            </table>

                            <!-- WHAT TO EXPECT -->
                            <h3 style="margin: 0 0 20px 0; font-size: 20px; font-weight: 600; color: #333333; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;" class="dark-mode-text">
                                What to Expect
                            </h3>

                            <table border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 15px 0; border-bottom: 1px solid #e5e5e5;" class="dark-mode-border">
                                        <h4 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: #333333; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;" class="dark-mode-text">
                                            📧 Daily Updates
                                        </h4>
                                        <p style="margin: 0; font-size: 14px; line-height: 20px; color: #666666; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;" class="dark-mode-text">
                                            Receive curated AWS news and updates every weekday morning
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px 0; border-bottom: 1px solid #e5e5e5;" class="dark-mode-border">
                                        <h4 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: #333333; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;" class="dark-mode-text">
                                            🎯 Personalized Content
                                        </h4>
                                        <p style="margin: 0; font-size: 14px; line-height: 20px; color: #666666; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;" class="dark-mode-text">
                                            Only news relevant to your selected AWS service categories
                                        </p>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="padding: 15px 0;">
                                        <h4 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 600; color: #333333; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;" class="dark-mode-text">
                                            🚀 Breaking News
                                        </h4>
                                        <p style="margin: 0; font-size: 14px; line-height: 20px; color: #666666; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;" class="dark-mode-text">
                                            Important AWS announcements and service launches as they happen
                                        </p>
                                    </td>
                                </tr>
                            </table>

                            <!-- CTA BUTTONS -->
                            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                <tr>
                                    <td align="center" style="padding: 20px 0;">
                                        <table border="0" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="border-radius: 6px; background-color: #FF9900; padding: 0 20px 0 0;">
                                                    <a href="#" target="_blank" style="font-size: 16px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #ffffff; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #FF9900; display: inline-block; font-weight: 600;">
                                                        Manage Subscription
                                                    </a>
                                                </td>
                                                <td style="border-radius: 6px; background-color: transparent;">
                                                    <a href="#" target="_blank" style="font-size: 16px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #FF9900; text-decoration: none; border-radius: 6px; padding: 12px 24px; border: 1px solid #FF9900; display: inline-block; font-weight: 600;">
                                                        Visit Website
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>

                        </td>
                    </tr>
                </table>
            </td>
        </tr>

        <!-- FOOTER -->
        <tr>
            <td bgcolor="#f5f5f5" align="center" style="padding: 30px 10px 30px 10px;" class="dark-mode-bg">
                <table border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px;">
                    <tr>
                        <td align="center">
                            <p style="margin: 0; font-size: 12px; line-height: 18px; color: #999999; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;" class="dark-mode-text">
                                You're receiving this email because you subscribed to SUO-AWS updates.<br>
                                <a href="#" target="_blank" style="color: #999999; text-decoration: underline;">
                                    Unsubscribe
                                </a> | 
                                <a href="#" target="_blank" style="color: #999999; text-decoration: underline;">
                                    Update Preferences
                                </a>
                            </p>
                            <p style="margin: 15px 0 0 0; font-size: 12px; line-height: 18px; color: #999999; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;" class="dark-mode-text">
                                © 2025 SUO-AWS. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>

    </table>

</body>
</html>`;

    const params = {
        Source: FROM_EMAIL,
        Destination: { ToAddresses: [email] },
        Message: {
            Subject: { Data: 'Welcome to SUO-AWS! 🎉' },
            Body: { Html: { Data: htmlTemplate } }
        }
    };

    await sesClient.send(new SendEmailCommand(params));
}

exports.handler = async (event) => {
    try {
        const { name, email, categories } = validateInput(JSON.parse(event.body));
        
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
        
        await sendWelcomeEmail(name, email, categories);
        
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
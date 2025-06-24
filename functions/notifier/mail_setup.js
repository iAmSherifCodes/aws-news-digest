import nodemailer from "nodemailer";

const transporter = nodemailer.createTransport({
  service: process.env.EMAIL_SERVICE || "gmail",
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS,
  },
});


export const sendEmail = async (from_name, from_email, to_name, to_email, subject, text, html) => {
 try {
    const info = await transporter.sendMail({
      from: `"${from_name}" <${from_email}>`,
      to: `"${to_name}" <${to_email}>`,
      subject: subject,
      text: text,
      html: html,
    });

    return {
      statusCode: 200,
      body: JSON.stringify(info),
    };
  } catch (error) {
    return {
      statusCode: 500,
      body: JSON.stringify(error),
    };
  }
};

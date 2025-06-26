# 🧪 Manual Testing Guide for News Processing Workflow

Welcome to the testing interface for our automated news processing system.  
This API allows you to manually trigger our workflow which performs:

1. 📰 **Scraping** the latest news  
2. 🗂 **Categorizing** the news  
3. 📣 **Notifying** subscribed users

The workflow normally runs daily, but you can test it manually by sending a request with a specific date.

---

## 🔗 API Endpoint

```
POST https://90kdndeozk.execute-api.us-east-1.amazonaws.com/dev/start-workflow
```

> Replace the URL with the one provided to you.

---

## 📥 Request Body

The API accepts a JSON body with an optional field:

| Field        | Type   | Description                          |
|--------------|--------|--------------------------------------|
| `target-date`| string | (Optional) Format: `MM/DD/YYYY`. If not provided, the system defaults to **yesterday**. |

### ✅ Example Payload

```json
{
  "target-date": "06/25/2025"
}
```

---

## 💻 Test with `curl`

You can test the API using the terminal:

```bash
curl -X POST https://90kdndeozk.execute-api.us-east-1.amazonaws.com/dev/start-workflow \
  -H "Content-Type: application/json" \
  -d '{"target-date": "06/25/2025"}'
```

Replace the URL and date as needed.

---

## 📫 Test with Postman

1. Open [Postman](https://www.postman.com/)

2. Click **New** → **HTTP Request**

3. Set method to **POST**

4. Enter the API URL:

   ```
   https://90kdndeozk.execute-api.us-east-1.amazonaws.com/dev/start-workflow
   ```

5. Go to the **Body** tab:

   * Choose `raw`
   * Choose `JSON` (from the dropdown on the right)
   * Paste this:

   ```json
   {
     "target-date": "06/25/2025"
   }
   ```

6. Click **Send**

---

## ✅ Sample Successful Response

```json
{
  "message": "Manual test has been triggered. Workflow started successfully."
}
```

You can use the `executionArn` to trace the process if needed (internally).

---

## ⚠️ Notes

* The system is case-sensitive. Field must be `target-date`, not `TargetDate` or `targetDate`.
* Please do not spam or test repeatedly within short time windows.
* Avoid using real dates where production data is sensitive — use test dates unless told otherwise.

---

## 🙋 Need Help?

If you face issues, please contact the project owner or support team.

---
## 🧪 Manual Testing Guide for News Processing Workflow

Welcome to the testing interface for our automated news processing system.  
This API allows you to manually trigger our workflow which performs:

1. 📰 **Scraping** the latest news  
2. 🗂 **Categorizing** the news  
3. 📣 **Notifying** subscribed users

The workflow normally runs daily, but you can test it manually by the API.

### Prerequisites
- Ensure that you have subscribed on [SUO-AWS website](https://suo-aws.vercel.app/)

### 🔗 API Endpoint

```
POST https://90kdndeozk.execute-api.us-east-1.amazonaws.com/dev/start-workflow
```

### Request Body

The API accepts an empty JSON body.
By default, the system processes news from yesterday, ensuring that subscribed users receive latest updates from the previous day.

#### Example Payload

```json
{}
```

### Test with `curl`

You can test the API using the terminal:

```bash
curl -X POST https://90kdndeozk.execute-api.us-east-1.amazonaws.com/dev/start-workflow \
  -H "Content-Type: application/json" \
  -d '{}'
```


### Test with Postman

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
   {}
   ```

6. Click **Send**

### Sample Successful Response

```json
{
  "message": "Manual test has been triggered. Workflow started successfully."
}
```

### Notes

* The system is case-sensitive. Field must be `target-date`, not `TargetDate` or `targetDate`.
* Please do not spam or test repeatedly within short time windows.
* Avoid using real dates where production data is sensitive — use test dates unless told otherwise.

---

## 🙋 Need Help?

If you face issues, please contact awofiranyesherif4@gmail.com.

---
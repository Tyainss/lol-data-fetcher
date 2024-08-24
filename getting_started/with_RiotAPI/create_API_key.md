### How to Create Your Riot API Key
To access Riot's API and start retrieving data (such as match history, player statistics, etc.), you'll need to create your Riot API key. Here's a step-by-step guide to help you get started:

---

#### Step 1: Create or Log in to Your Riot Developer Account
1. Go to the Riot Developer Portal: Navigate to [https://developer.riotgames.com/](https://developer.riotgames.com/).
2. Sign In: Log in using your existing Riot Games account (the same one you use for League of Legends).

#### Step 2: Generate a Developer API Key
1. Access the Developer Dashboard: Once you're in the developer portal, head to the API Keys section.
2. Generate a New Key: Under the “**Development API Key**” section, click on the “**Generate Key**” button. This will give you a **temporary API key** that lasts for 24 hours.

    - **Note**: This development key is for testing purposes and is limited to a certain number of requests per minute.

#### Step 3: Save and Use Your API Key

- **Save the Key**: Once generated, your API key will be displayed on the screen. Copy this key and store it securely, as it will be required for all your API requests.
- **Use the Key in Requests**: Replace `YOUR_API_KEY` in the `config_example.json` file for your new API Key

#### Step 4: Upgrade to Production API Key (Optional)
If you plan to use the API Key for more than extracting the code 1 time, and you plan to develop your own project or even complement this one, you can apply for a **Production API Key**
This envolves submitting a detailed request explaining your project's purpose and how you'll use the data

- **Requesting a Production Key**: In the developer portal, submit a request in the **Application Registration** section. Riot will review your application and, if approved, provide you with a key with elavated rate limits and permanent access
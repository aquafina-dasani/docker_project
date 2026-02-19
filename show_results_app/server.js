const express = require('express');
const axios = require('axios');
const { MongoClient } = require('mongodb');
const path = require('path');

const app = express();
const PORT = 3000;

const AUTH_SERVICE_URL = 'http://auth_service:5000/validate';
const MONGO_URL = 'mongodb://mongo:27017';
const MONGO_DB_NAME = 'projectdb';
const MONGO_COLLECTION_NAME = 'analytics';


app.use(express.urlencoded({ extended: true }));
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));


const mongoClient = new MongoClient(MONGO_URL);

async function connectToMongo() {
  try {
    await mongoClient.connect();
    console.log('Successfully connected to MongoDB');
  } catch (err) {
    console.error('Failed to connect to MongoDB', err);
    process.exit(1);
  }
}


app.get('/', (req, res) => {
  res.render('index', { error: null, result: null });
});


app.post('/show', async (req, res) => {
  const { username, password, metric } = req.body;

  try {
    await axios.post(AUTH_SERVICE_URL, { username, password });
  } catch (authError) {
    const errorMessage = 'Invalid username or password. Please try again.';
    res.status(401).render('index', { error: errorMessage, result: null });
    return;
  }


  try {
    const db = mongoClient.db(MONGO_DB_NAME);
    const collection = db.collection(MONGO_COLLECTION_NAME);

    const analyticsResult = await collection.findOne({ _id: metric });

    if (!analyticsResult) {
      const noDataMessage = `No analytics data found for the metric '${metric}'. Try submitting some data first.`;
      res.status(404).render('index', { error: noDataMessage, result: null });
      return;
    }

    res.render('index', { error: null, result: analyticsResult });

  } catch (dbError) {
    console.error('Database query failed:', dbError);
    const dbErrorMessage = 'An error occurred while fetching analytics data.';
    res.status(500).render('index', { error: dbErrorMessage, result: null });
  }
});


connectToMongo().then(() => {
    app.listen(PORT, () => {
        console.log(`show_results_app is listening on port ${PORT}`);
    });
});
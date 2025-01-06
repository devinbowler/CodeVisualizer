const express = require("express");
const { Pool } = require("pg");
const cors = require("cors");

require("dotenv").config(); // To load environment variables

const app = express();
const port = process.env.PORT || 3000;
app.use(cors());

// Set up PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL, // Get from environment variable
  ssl: { rejectUnauthorized: false }, // Required for Neon
});

// Middleware to parse JSON requests
app.use(express.json());

app.post("/loginUser", async (req, res) => {
  const { username, password } = req.body; // Extract username and password from request body
  try {
    const query = "SELECT * FROM users WHERE email = $1 AND password = $2;";
    const values = [username, password]; // Use parameterized query to prevent SQL injection
    const { rows } = await pool.query(query, values);

    if (rows.length > 0) {
      res.status(200).json({ success: true, message: "Login successful!" });
    } else {
      res.status(401).json({ success: false, message: "Invalid username or password." });
    }
  } catch (error) {
    console.error("Database query error:", error);
    res.status(500).json({ success: false, error: "Internal Server Error" });
  }
});

app.post("/registerUser", async (req, res) => {
  const { username, password } = req.body; // Extract username and password
  try {
    if (!username || !password) {
      return res.status(400).json({ success: false, message: "Username and password are required" });
    }

    console.log("Registering user:", username, password);

    const query = "INSERT INTO users (email, password) VALUES ($1, $2);";
    const values = [username, password];
    await pool.query(query, values);

    res.status(200).json({ success: true, message: "Registration successful!" });
  } catch (error) {
    console.error("Database query error:", error.stack);
    res.status(500).json({ success: false, error: "Internal Server Error" });
  }
});

// Start the server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
 

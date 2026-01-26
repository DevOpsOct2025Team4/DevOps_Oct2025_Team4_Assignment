const express = require("express");

const router = express.Router();

router.get("/hello", (req, res) => {
    res.json({ message: "Hello from Express!" });
});

module.exports = router;

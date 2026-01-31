const express = require("express");
const { PrismaClient } = require("@prisma/client");

const router = express.Router();
const prisma = new PrismaClient();

router.get("/hello", (req, res) => {
  res.json({ message: "Hello from Express!" });
});

router.get("/health", async (req, res) => {
  let database = false;

  try {
    await prisma.user.findMany({ take: 1 });
    database = true;
  } catch (error) {
    console.error("DB healthcheck failed:", error.message);
  }

  res.json({
    server: true,
    database,
  });
});

module.exports = router;

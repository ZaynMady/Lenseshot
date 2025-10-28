import express from "express";
import cors from "cors";
import bodyParser from "body-parser";
import puppeteer from "puppeteer";

const app = express();
const port = 4000;

app.use(cors());
app.use(bodyParser.json({ limit: "10mb" }));

app.post("/api/export/pdf", async (req, res) => {
  const { filename, html } = req.body;

  if (!filename || !html) {
    return res.status(400).json({ msg: "filename and html are required" });
  }

  try {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.setContent(html, { waitUntil: "domcontentloaded" });

    const pdfBuffer = await page.pdf({
      format: "A4",
      printBackground: true,
    });

    await browser.close();

    res.set({
      "Content-Type": "application/pdf",
      "Content-Disposition": `attachment; filename="${filename}.pdf"`,
    });
    res.send(pdfBuffer);
  } catch (err) {
    console.error(err);
    res.status(500).json({ msg: "Error generating PDF" });
  }
});

app.listen(port, () => console.log(`Server running on port ${port}`));

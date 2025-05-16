import express from "express";
import multer, { diskStorage } from "multer";
import { join, dirname } from "path";
import { fileURLToPath } from "url";
import fs from "fs";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();
const port = 3000;

const UPLOADS_DIR = join(__dirname, "uploads/");

if (!fs.existsSync(UPLOADS_DIR)) {
  try {
    fs.mkdirSync(UPLOADS_DIR, { recursive: true });
    console.log(`上传目录已创建: ${UPLOADS_DIR}`);
  } catch (err) {
    console.error(`创建上传目录失败: ${UPLOADS_DIR}`, err);
    process.exit(1);
  }
}

const storage = diskStorage({
  destination: function (_req, _file, cb) {
    cb(null, UPLOADS_DIR);
  },
  filename: function (_req, file, cb) {
    cb(null, file.originalname);
  },
});

const upload = multer({
  storage: storage,
});

app.post("/api/upload", (req, res, _next) => {
  upload.single("file")(req, res, (err) => {
    if (err instanceof multer.MulterError) {
      console.error("Multer error:", err);
      return res.status(400).json({ message: `文件上传发生 Multer 错误: ${err.message}` });
    } else if (err) {
      console.error("Upload error:", err);
      return res.status(500).json({ message: err.message || "文件上传失败，请检查服务器日志。" });
    }

    if (!req.file) {
      return res.status(400).json({ message: "没有选择文件或文件上传失败。" });
    }

    console.log("文件已成功上传:", req.file);
    res.status(200).json({
      message: "文件上传成功",
      filename: req.file.filename,
      path: req.file.path,
    });
  });
});

app.use((err, _req, res, _next) => {
  console.error("服务器未捕获错误:", err.stack || err.message || err);
  res.status(err.status || 500).json({
    message: err.message || "服务器内部发生未知错误",
  });
});

app.listen(port, () => {
  console.log(`服务器运行在 http://localhost:${port}`);
  console.log(`文件将上传到: ${UPLOADS_DIR}`);
});

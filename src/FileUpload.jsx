// src/components/FileUpload.jsx
import { useState, useCallback, useRef } from "react";
import "./FileUpload.css";

const FileUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [uploadProgress, setUploadProgress] = useState(0);

  const fileInputRef = useRef(null);

  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
    setUploadStatus("");
    setUploadProgress(0);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      setSelectedFile(file);
      e.dataTransfer.clearData();
    }
  }, []);

  const handleFileSelectChange = (e) => {
    setUploadStatus("");
    setUploadProgress(0);
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      setSelectedFile(file);
    }
  };

  const onAreaClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadStatus("请先选择一个文件。");
      return;
    }

    setUploadStatus("上传中...");
    setUploadProgress(0);

    const formData = new FormData();
    formData.append("file", selectedFile);

    const API_ENDPOINT = "/api/upload";

    try {
      const xhr = new XMLHttpRequest();

      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const percentComplete = Math.round((event.loaded / event.total) * 100);
          setUploadProgress(percentComplete);
        }
      };

      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          const response = JSON.parse(xhr.responseText);
          setUploadStatus(`上传成功: ${response.message || "文件已处理"}`);
          setSelectedFile(null);
        } else {
          let errorMsg = `服务器错误: ${xhr.status}`;
          try {
            const errorResponse = JSON.parse(xhr.responseText);
            errorMsg = errorResponse.message || errorMsg;
          } catch (e) {}
          setUploadStatus(`上传失败: ${errorMsg}`);
          console.error("上传错误详情:", xhr.responseText);
        }
      };

      xhr.onerror = () => {
        setUploadStatus("上传失败: 网络错误或服务器无响应。");
        console.error("网络错误");
      };

      xhr.open("POST", API_ENDPOINT, true);
      xhr.send(formData);
    } catch (error) {
      setUploadStatus(`上传出错: ${error.message}`);
      console.error("上传过程中发生代码错误:", error);
    }
  };

  return (
    <div className="file-upload-container">
      <h3>拖拽文件到这里或点击选择</h3>
      <div
        className={`drop-zone ${isDragging ? "dragging" : ""}`}
        onDragEnter={handleDragEnter}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={onAreaClick}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelectChange}
          style={{ display: "none" }}
        />
        {selectedFile ? (
          <p className="file-name">已选择: {selectedFile.name}</p>
        ) : (
          <p>将文件拖到此处，或点击选择文件</p>
        )}
      </div>

      {selectedFile && (
        <div className="file-actions">
          <button onClick={handleUpload} className="upload-button">
            上传文件
          </button>
        </div>
      )}

      {uploadStatus && (
        <p
          className={`upload-status ${
            uploadStatus.includes("失败") || uploadStatus.includes("错误") ? "error" : "success"
          }`}
        >
          {uploadStatus}
        </p>
      )}

      {uploadProgress > 0 && uploadStatus.includes("上传中") && (
        <div className="progress-bar-container">
          <div className="progress-bar" style={{ width: `${uploadProgress}%` }}>
            {uploadProgress}%
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;

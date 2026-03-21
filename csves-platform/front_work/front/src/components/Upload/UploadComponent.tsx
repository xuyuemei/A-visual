import React, { useEffect, useState } from "react";
import styles from "./UploadComponent.module.css";
import { MenuProps, Dropdown, Button, message ,Spin} from "antd";
import { CopyOutlined ,LoadingOutlined} from "@ant-design/icons";
import exampleImage from "../../assets/example/image.png"; // 示例图片路径

const fileTypes = {
  image: [".png", ".jpg", ".jpeg"],
  file: [".xlsx", ".csv", ".json", ".jsonl"],
};

type Tab = "text" | "image" | "file";

function UploadComponent({ onUploadSuccess }: { onUploadSuccess: (data: any) => void }) {
  const [activeTab, setActiveTab] = useState<Tab>("text");
  const [file, setFile] = useState<File | null>(null);
  const [textInput, setTextInput] = useState("");
  const [isDragging, setIsDragging] = useState(false); // 拖拽状态
  const [isExampleFile, setIsExampleFile] = useState(false); // 是否示例文件
  const [exampleFileName, setExampleFileName] = useState(""); // 示例文件名


  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      // console.log("选中的文件：", selectedFile);
      // setTimeout(() => {
      //   upload(); // 选完文件自动上传
      // }, 0);
    }
  };
  
  // 拖拽相关处理
  const handleDragOver = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(true); // 开始拖拽时，设置isDragging为true
  };

  const handleDragLeave = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false); // 离开拖拽区域时，设置isDragging为false
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false); // 完成放置后，重置isDragging为false

    const droppedFiles = event.dataTransfer.files;
    console.log("拖拽的文件：", droppedFiles);

    const exampleFile = event.dataTransfer.getData("exampleFile");
    if (exampleFile) {
      // 是示例文件
      console.log("拖拽的是示例文件：", exampleFile);
      setIsExampleFile(true);
      setExampleFileName(exampleFile);
      return;
    }
    
    if (droppedFiles.length > 0) {
      const validTypes = activeTab === "image" ? fileTypes.image : fileTypes.file;
      const fileExtension = droppedFiles[0].name.includes('.') ? '.' + droppedFiles[0].name.split('.').pop()?.toLowerCase() : '';

      if (fileExtension && validTypes.includes(fileExtension)) {
        console.log("选中的文件droppedFiles：", droppedFiles);
        setIsExampleFile(false);
        setFile(droppedFiles[0]); // 处理拖拽到区域的文件
        console.log("处理拖拽到区域的文件：", file); // 打印文件后缀名
      } else {
        // 如果文件类型不匹配，弹出提示框
        alert(`文件类型不符合要求，请上传以下格式的文件：${validTypes.join(', ')}`);
      }
  
    }
  };

  const renderUploadSection = () => {
    if (activeTab === "text") {
      return (
        <textarea
          className={styles.input}
          placeholder="请输入包含待分析数据的文本"
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
        />
      );
    }

    if (activeTab === "image" || activeTab === "file") {
      const acceptTypes = activeTab === "image" ? fileTypes.image : fileTypes.file;

      return (
        <div
          className={`${styles.area} ${isDragging ? styles.dragging : ""}`} // 根据isDragging状态添加class
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById("fileInput")?.click()} // 点击div触发input
        >
          <input
            id="fileInput"
            type="file"
            accept={acceptTypes.join(",")}
            style={{ display: "none" }}
            onChange={handleFileChange}
          />
          <div className={styles.icon}>
            {activeTab === "image" ? "🖼️" : "📄"}
          </div>
          <div className={styles.text}>
            {activeTab === "image"
              ? "请点击或拖拽上传包含待分析数据的图片（支持png, jpg, jpeg）"
              : "请点击或拖拽上传包含待分析数据的文件（支持xlsx, csv, json, jsonl）"}
            <br />
          </div>
        </div>
      );
    }
  };

  const examples = {
    text: `公司近3年经营情况：2022年营收4000万，利润600万，市场业务占比70%；2023年营收4200万，利润600万，市场业务占比83%；2024年营收目标8000万，利润预计700万，市场业务预计占比 75%。`,
    image: `请上传jpg/png格式图片，示例图大小建议不超过2MB。`,
    file: `请上传xlsx/csv/json格式文件，示例内容包含待分析的数据。`,
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(examples[activeTab]);
      message.success("复制成功！");
    } catch (err) {
      message.error("复制失败，请手动复制！");
    }
  };

  const dropdownContent = (
    <div className={styles.dropdownContent}>
      {activeTab === "text" ? (
        <>
          <div className={styles.dropdownHeader}>
            文本示例
            <Button
              type="link"
              icon={<CopyOutlined />}
              onClick={handleCopy}
              className={styles.copyButton}
            >
              复制
            </Button>
          </div>
          <div className={styles.dropdownBody}>{examples[activeTab]}</div>
        </>
      ) : (
        <>
          <div className={styles.dropdownHeader}>
            {activeTab === "image" ? "图片示例（可拖拽图片至上传框内）" : "文件示例"}
          </div>
          <div
            className={styles.previewArea}
          >
            {activeTab === "image" ? (
              <img
                src={exampleImage} // 换成你的示例图片路径
                alt="示例图片"
                draggable
                className={styles.previewImage}
              />
            ) : (
            <div>
              <div className={styles.fileIcon} draggable   onDragStart={(e) => {
                e.dataTransfer.setData("exampleFile", "data_process"); 
              }}
            >📄 数据处理示例文件.xlsx </div>
              <div className={styles.fileIcon} draggable   onDragStart={(e) => {
                e.dataTransfer.setData("exampleFile", "data_calculation"); 
              }}
            >📄 数据计算示例文件.xlsx </div>
              <div className={styles.fileIcon} draggable   onDragStart={(e) => {
                e.dataTransfer.setData("exampleFile", "data_analysis"); 
              }}
            >📄 数据分析示例文件.xlsx </div>
            </div>

            
            )}
          </div>
        </>
      )}
    </div>
  );


  const [spinning, setSpinning] = React.useState(false);

  const upload = async () => {
    setSpinning(true);

    const formData = new FormData();
  
    if (activeTab === "text") {
      formData.append("text", textInput);
    } else if (isExampleFile) {
      formData.append("exampleFile", exampleFileName); // 只传文件名
    } else if (file) {
      formData.append("file", file); // 传真实文件
    }
    
    try {
      console.log("上传的文件：",exampleFileName, file);
      const response = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });
  
      if (!response.ok) {
        throw new Error("上传失败a");
      }
  
      // 判断是否有返回内容
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        const result = await response.json();
        console.log("上传成功，返回：", result);
        onUploadSuccess(result);  // 上传成功，回传数据给Workbook
      } else {
        console.log("上传成功（无返回内容）");
        message.success("上传成功（无返回内容）");
        }
    } catch (error) {
      console.error("上传失败：", error);
      message.error("上传失败，请稍后重试,错误原因："+error);  // 失败弹窗
      } finally {
      setSpinning(false); // 无论成功失败，都取消 loading
      setIsExampleFile(false); // 重置示例文件名
    }
  
  };

  useEffect(() => {
    if (file) {
      console.log("检测到真实文件上传：", file);
      upload();
    }
  }, [file]);
  
  useEffect(() => {
    if (isExampleFile && exampleFileName) {
      console.log("检测到示例文件上传：", exampleFileName);
      upload();
    }
  }, [exampleFileName, isExampleFile]);
    
    
  

  return (
    
    <div className={styles.container}>
      <div style={{ display: "flex" }}>
        <div className={styles.buttons}>
          <button
            className={activeTab === "text" ? styles.active : styles.button}
            onClick={() => setActiveTab("text")}
          >
            文本输入
          </button>

          <button
            className={activeTab === "image" ? styles.active : styles.button}
            onClick={() => setActiveTab("image")}
          >
            图片上传
          </button>

          <button
            className={activeTab === "file" ? styles.active : styles.button}
            onClick={() => setActiveTab("file")}
          >
            文件上传
          </button>
        </div>
        <>  
      <Spin spinning={spinning} indicator={<LoadingOutlined style={{ fontSize: 68 }} spin />} fullscreen tip="文件上传中"/>
    </>

        <div className={styles.buttonGroup}>
        {activeTab === "text" && (
          <Button className={styles.confirm }  onClick={upload}>确认输入</Button>
        )}
        <Dropdown
          placement="topRight"
          dropdownRender={() => dropdownContent}
          arrow={{ pointAtCenter: true }}
        >
          <Button className={styles.example}>查看示例</Button>
        </Dropdown>
      </div>
      </div>

      <div className={styles.section}>{renderUploadSection()}</div>
    </div>
  );
};

export default UploadComponent;

import React, { useEffect, useState,useRef } from "react";
import styles from "./Graph.module.css";
// import RefPrompts from '../../components/RefPrompts/RefPrompts';
import { Flex, Splitter, Button ,Divider,Row,Col, message } from 'antd';
import { Select, Card, ConfigProvider, Space, theme, Dropdown } from 'antd';
import { DownOutlined,RobotOutlined, DownloadOutlined, UserOutlined ,HeartOutlined} from '@ant-design/icons';
import type { WorkbookInstance } from '@fortune-sheet/react';
import Palette from '../../components/Palette/Palette';
import {
    // 消息气泡
    Bubble,
    // 发送框
    Sender,
  } from '@ant-design/x';
import ModalImage from "react-modal-image";
import axios from 'axios';

interface TemplateData {
  Template_ID: number;
  Template_code: string;
  Template_graph: string; // base64 图像
}

 function Graph({ getRef }: { getRef: () => React.RefObject<WorkbookInstance | null> }) {
      const ref = getRef();
      const [inputValue, setInputValue] = useState<string>('');
      const [selectedModel, setSelectedModel] = useState<string>('1');
      const [selectedColor, setSelectedColor] = useState<string[]>(['#EAF3EA', '#ECF3FD', '#E1D5E7', '#CCE4FF']);
      const [selectedType, setSelectedType] = useState<string>('折线图');
      const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
      const [historyCode, setHistoryCode] = useState<string | null>(null);
      // const [generatedImage, setGeneratedImage] = useState<string | null>(null);
      // const [isGenerated, setIsGenerated] = useState<boolean>(true);
      const [messages, setMessages] = useState<any[]>([]);
      const scrollRef = useRef<HTMLDivElement>(null);
      const [selectedId, setSelectedId] = useState<number | null>(null);



      useEffect(() => {
        const div = scrollRef.current;
        if (div) {
          div.scrollTop = div.scrollHeight;
        }
      }, [messages]);

      const [templates, setTemplates] = useState<TemplateData[]>([]);

      useEffect(() => {
        console.log("templates:",templates)
        axios.get(`http://localhost:8000/api/templates?chart_type=${selectedType}`)
          .then(response => {
            console.log(response.data)
            setTemplates(response.data);
            
          })
          .catch(error => {
            console.error('获取模板数据失败:', error);
          });
      }, [selectedType]);

      const tabList = [
      {
          key: 'tab1',
          tab: '热门模板',
      },
      {
          key: 'tab2',
          tab: '我的收藏',
      },
      ];
      const [activeTabKey1, setActiveTabKey1] = useState<string>('tab1');
      const onTab1Change = (key: string) => {
      setActiveTabKey1(key);
    };

     


    const contentList: Record<string, React.ReactNode> = {
    tab1: (    <div   style={{ overflowX: 'auto' }}>
      <Row
        gutter={12}
        style={{
          display: 'flex',
          flexWrap: 'nowrap', // ❗ 不换行，横向排列
          minWidth: 'max-content',
          height:'300px'
        }}
      >

      {Array.isArray(templates) && templates.length > 0 ? (
        templates.map(template => (
          <Col key={template.Template_ID} span={8} style={{ flex: '0 0 auto' , padding: '6px,6px'}}>
            <div style={{ 
              background: '#f0f2f5', 
              padding: '6px,6px', 
              height: '100%', 
              width: '380px', 
              display: 'flex', 
              flexDirection: 'column', 
              justifyContent: 'center', 
              alignItems: 'center' 
            }}
            className={`${styles.templateImg} ${selectedId === template.Template_ID ? styles.selected : ''}`}>
              <img
              src={`data:image/png;base64,${template.Template_graph}`}
              alt={`Template ${template.Template_ID}`}
              style={{ width: '100%', height: '90%', objectFit: 'contain' }}
              onClick={() => {  if (selectedId === template.Template_ID) {
                  setSelectedId(null); // 再次点击取消选择
                  setSelectedTemplate(null)
                } else {
                  setSelectedId(template.Template_ID);
                  setSelectedTemplate(template.Template_code)
                }
              }}
              />
              {/* <div style={{ fontSize: 12, marginTop: 4 }}>模板 ID: {template.Template_ID}</div> */}
            </div>
          </Col>
        ))
      ) : (
        <div style={{ marginLeft: 20 ,fontSize:'16px'}}>暂无可用模板</div>
      )}

      </Row>
    </div>
    
),
    tab2: <p>content2</p>,
  };

    const handleColorSelect = (colors: string[]) => {
    setSelectedColor(colors);
    console.log('当前选中颜色:', colors);
  };

  function createImageMessage(imgData: string, code: string) {
  return {
    id: String(Date.now()),
    placement: 'start',
    role: 'bot',
    avatar: {
      icon: <RobotOutlined />,
      style: {
        color: '#f56a00',
        backgroundColor: '#fde3cf',
      },
    },
    content: (
      <ModalImage
        small={`data:image/png;base64,${imgData}`}
        large={`data:image/png;base64,${imgData}`}
        alt="图表"
        className={styles.imgsize}
      />
    ),
    footer: (
      <Space size="small">
        <Dropdown.Button
          type="default"
          size="small"
          menu={{
            items: [
              { key: '1', label: '收藏至历史图表' },
              { key: '2', label: '收藏至我的模板' },
            ],
            onClick: async (e) => {
              const chartData = {
                Chart_type: selectedType,
                Template_code: code,
                Template_graph: imgData,
              };

              try {
                if (e.key === '1') {
                  const res = await fetch('http://localhost:8000/api/history_charts', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(chartData),
                  });
                  const result = await res.json();
                  console.log('添加到历史图表:', result);
                } else if (e.key === '2') {
                  const res = await fetch('http://localhost:8000/api/templates', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(chartData),
                  });
                  const result = await res.json();
                  console.log('收藏为模板:', result);
                  message.success("收藏模板成功！");
                }
              } catch (error) {
                console.error('收藏失败:', error);
              }
            },
          }}
        >
          <HeartOutlined />
        </Dropdown.Button>

        <Button
          type="default"
          size="small"
          onClick={handleDownload}
          icon={<DownloadOutlined />}
        />
      </Space>
    ),
  };
}


  function createUserMessage(InputValue: string) {
      return {
        id: String(Date.now()), // 唯一ID，避免重复
        // type: 'text',
        placement:'end',
        role: 'user',
        avatar: {
          icon: <UserOutlined />,
          style: {
            color: '#fff',
            backgroundColor: '#87d068',
          },
        },
        content: InputValue
    }
  }
    

  const [loading, setLoading] = useState<boolean>(false);
      const submit = async () => {

        const formData = new FormData();
  
        // 校验 inputValue
        if (!inputValue || inputValue.trim() === "") {
          message.error("请输入内容");
          return;
        }
  
        // 获取表格数据
        const sheetData = ref.current?.getSheet().celldata;
        if (!sheetData) {
          message.error("数据为空！");
          return;
        }

        if(messages.length>0){
          setMessages((prev) => [...prev, createUserMessage(inputValue)]);
        }
  
        // 组装 FormData
        formData.append("data", JSON.stringify(sheetData));
        formData.append("type", selectedType);
        formData.append("inputValue", inputValue);
        formData.append("color", JSON.stringify(selectedColor)); 
        formData.append("selectedModel", selectedModel); // 保留模型字段
        formData.append("template", selectedTemplate?? ''); // 保留模型字段
        formData.append("history_code", historyCode?? ''); // 保留模型字段
  
        console.log("上传的表格数据：", formData);
  
        try {
          // console.log("上传的文件：",exampleFileName, file);
          const response = await fetch("http://localhost:8000/api/chart", {
            method: "POST",
            body: formData,
          });
      
          if (!response.ok) {
            throw new Error("上传失败a");
          }
      
          // 判断是否有返回内容
          const contentType = response.headers.get("content-type");
          if (contentType && contentType.includes("application/json")) {
            message.success("生成成功！");
            const result = await response.json();
            console.log("上传成功，返回：", result);
            setHistoryCode(result.code);
            // setGeneratedImage(result.img_base64);
            setMessages((prev) => [...prev, createImageMessage(result.img_base64,result.code)]);
          } else {
            console.log("上传成功（无返回内容）");
            message.success("上传成功（无返回内容）");
            }
        } catch (error) {
          console.error("上传失败：", error);
          message.error("上传失败，请稍后重试,错误原因："+error);  // 失败弹窗
          } finally {
          setLoading(false); // 无论成功失败，都取消 loading
          // setIsExampleFile(false); // 重置示例文件名
        }
      
      };

      const handleDownload = () => {
        console.log(messages)
        // const link = document.createElement('a');
        // link.href = `data:image/png;base64,${generatedImage}`; // 换成你的图片地址
        // link.download = 'chart.png';
        // link.click();
    };

 return (
 <div className={styles.content} >
    {messages.length>0  ? (
      <div style={{ maxHeight: 500, overflowY: 'auto' }} ref={scrollRef}>
        <Bubble.List items={messages[0] ? messages : messages.slice(1)} />
        {/* <Button onClick={() => setIsGenerated(false)}>返回</Button> */}
      </div>
    ) : (<div >
      <div style={{ display: 'flex', justifyContent: 'space-between',  gap: 11, marginBottom: 16, color:'GrayText' }}>
        {/* 图表类型选择 */}
        <div >
          <div >图表类型</div>
          <Select
            style={{
              width: '148px' ,
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
              borderRadius: 4,
              color: '#ffffff',
              marginRight: 48,
            }}
            dropdownStyle={{ color: '#000000' }}
            defaultValue="折线图"
            options={[
              { value: '折线图', label: '折线图' },
              { value: '柱状图', label: '柱状图' },
              { value: '堆叠图', label: '堆叠图' },
              { value: '饼图', label: '饼图' },
              { value: '雷达图', label: '雷达图' },
              { value: '热力图', label: '热力图' },
              { value: '漏斗图', label: '漏斗图' },
              { value: '散点图', label: '散点图' },
              { value: '仪表盘', label: '仪表盘' },
              { value: 'K线图', label: 'K线图' },
              { value: '长图表', label: '长图表' },
              { value: '区域图', label: '区域图' },
              { value: '面积热力图', label: '面积热力图' },
              { value: '三维散点图', label: '三维散点图' },
            ]}
            onChange={value => {
              console.log('Selected chart type:', value);
              setSelectedType(value);
            }}
          />
        </div>

        {/* 配色风格选择 */}
        <div style={{  width: '300px' }}>
          <div >配色风格 </div>
            <Palette onColorSelect={handleColorSelect} />
        </div>
      </div>

      <div>
      {/* <div style={{ padding: '0px 0px 4px' }}> 模板选择 </div> */}
      {/* <Divider style={{ borderColor: 'grey' , color:"grey"}} type="horizontal" orientation="left">模板选择</Divider> */}
      <div style={{ marginBottom: 4 , color:'GrayText'}}>模板选择 </div>
        <Card
        style={{ width: '100%' , boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',padding: '0px 0px 2px'}}
        // title="模板选择"
        // extra={<a href="#">查看更多</a>}
        tabList={tabList}
        activeTabKey={activeTabKey1}
        onTabChange={onTab1Change}
      >
        {contentList[activeTabKey1]}
      </Card>

      </div> 

    </div>
  )}
      <Sender 
    className={styles.sender}
    autoSize={{ minRows: 2, maxRows: 6 }}
    placeholder="输入你想生成的图表描述，开始生成图表吧！"
    onChange={(val) => setInputValue(val)}
    footer={({ components }) => {
      const { SendButton, LoadingButton } = components;
      return (
        // <Flex justify="space-between" align="center">
          <Flex justify="flex-end" align="center" gap={4}>
              {messages.length > 0 && (
                <Button onClick={() => setMessages([])}>开启新对话</Button>
              )}
                    <Select
                    style={{ width: 145 }}
                showSearch
                placeholder="模型选择"
                filterOption={(input, option) =>
                  (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
                }
                onChange={(value) => {
                console.log("Selected model:", value);
                setSelectedModel(value); // Update the state with the selected value
              }}
                defaultActiveFirstOption
                options={[
                  { value: '1', label: 'gpt-4o' },
                  { value: '2', label: 'deepseek-r1' },
                  { value: '3', label: 'deepseek-v3' },
                  { value: '4', label: 'baichuan2 (free)' },
                ]}
              />
      <Divider type="vertical" />
            {loading ? (
              <LoadingButton type="default" />
            ) : (
              <SendButton type="primary" disabled={false} />
            )}
          </Flex>
        // {/* </Flex> */}
      );
    }}
    onSubmit={() => {
      submit()
      setLoading(true);
    }}
    onCancel={() => {
      setLoading(false);
    }}
    actions={false}

    />

  </div>
  );
};

export default Graph;

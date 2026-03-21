import React, { useEffect, useState } from "react";
import styles from "./DataProcess.module.css";
// import RefPrompts from '../../components/RefPrompts/RefPrompts';
import { Flex, Splitter, Button ,Divider,Row,Col, message } from 'antd';
import { Select, Card, ConfigProvider, Space, theme } from 'antd';
import { FireOutlined, ReadOutlined, RocketOutlined } from '@ant-design/icons';
import { Prompts, PromptsProps, Sender } from '@ant-design/x';
import type { WorkbookInstance } from '@fortune-sheet/react';

  
function DataProcess({ getRef }: { getRef: () => React.RefObject<WorkbookInstance | null> }) {
  const ref = getRef();
  const [loading, setLoading] = useState<boolean>(false);
  const [inputValue, setInputValue] = useState<string>('');
  const [selectedModel, setSelectedModel] = useState<string>('1'); // 默认选择第一个模型
  const promptMap: Record<string, string> = {
  '1-1': '请帮我清洗这份表格，处理缺失值、格式不一致和异常值。',
  '1-2': '帮我筛选出年龄大于30且收入高于5万的记录。',
  '1-3': '请删除这张表中重复的记录，仅保留唯一项。',
  '2-1': '请统计每个部门的总销售额。',
  '2-2': '按城市分组，统计每个城市的平均订单金额。',
  '2-3': '计算性别为女性、年龄在25到35岁之间用户的平均活跃天数。',
  '3-1': '请分析订单量和广告点击数之间的关系。',
  '3-2': '找出影响用户留存率的最相关指标。',
  '3-3': '用线性回归模型预测用户在下月的消费金额。',
};


  const renderTitle = (icon: React.ReactElement, title: string) => (
    <Space align="start">
      {icon}
      <span>{title}</span>
    </Space>
  );
  
  const items: PromptsProps['items'] = [
    {
      key: '1',
      label: renderTitle(<FireOutlined style={{ color: '#FF4D4F' }} />, '表格处理'),
      
      children: [
        {
          key: '1-1',
          description: `数据清洗`,
        },
        {
          key: '1-2',
          description: `数据筛选`,
        },
        {
          key: '1-3',
          description: `数据去重`,
        },
      ],
    },
    {
      key: '2',
      label: renderTitle(<ReadOutlined style={{ color: '#1890FF' }} />, '数据计算'),
      // description: 'How to design a good product?',
      children: [
        {
          key: '2-1',
          // icon: <HeartOutlined />,
          description: `数据求和`,
        },
        {
          key: '2-2',
          // icon: <SmileOutlined />,
          description: `分组计算`,
        },
        {
          key: '2-3',
          // icon: <CommentOutlined />,
          description: `条件计算`,
        },
      ],
    },
    {
      key: '3',
      label: renderTitle(<RocketOutlined style={{ color: '#722ED1' }} />, '数据分析'),
      // description: 'How to start a new project?',
      children: [
        {
          key: '3-1',
          label: '关联分析',
          // description: `Install Ant Design X`,
        },
        {
          key: '3-2',
          label: '相关性分析',
          // description: `Play on the web without installing`,
        },
        {
          key: '3-3',
          label: '回归分析',
          // description: `Play on the web without installing`,
        },

      ],
    },
  ];

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
        message.error("请先选择数据表格");
        return;
      }

      // 组装 FormData
      formData.append("inputValue", inputValue);
      formData.append("selectedModel", selectedModel); // 保留模型字段
      formData.append("sheetData", JSON.stringify(sheetData));

      console.log("上传的表格数据：", formData);

      try {
        // console.log("上传的文件：",exampleFileName, file);
        const response = await fetch("http://localhost:8000/api/dataprocess", {
          method: "POST",
          body: formData,
        });
    
        if (!response.ok) {
          throw new Error("上传失败a");
        }
    
        // 判断是否有返回内容
        const contentType = response.headers.get("content-type");
        if (contentType && contentType.includes("application/json")) {
          message.success("处理成功！");
          const result = await response.json();
          console.log("上传成功，返回：", result);

          const sheets = JSON.parse(JSON.stringify(ref.current?.getAllSheets() || '[]')) as { id: string }[];
          console.log("sheets:",sheets)
          const hasId2 = sheets.some((sheet: { id: string }) => sheet.id === "2");

          if (!hasId2) {
            ref.current?.addSheet("2");
          }

          ref.current?.activateSheet({ id: "2" });
          ref.current?.updateSheet([
          {
            id: "2",
            name: "新数据",
            celldata: result?.celldata,
            order: 0,
          },
            ]);
          ref.current?.setSheetName("处理数据");
          


          // onUploadSuccess(result);  // 上传成功，回传数据给Workbook
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

  return (
    
    <div className={styles.content}>
        {/* <RefPrompts></RefPrompts> */}
        <div style={{ color: 'grey', fontSize: '16px', marginBottom: '10px' , marginTop: '16px'}}>你想如何处理数据？（结合数据上传栏示例文件使用更佳）</div>

        <ConfigProvider>
            <Prompts
          className={styles.prompts}
          style={{ marginTop: '16px' }}
                // title="你想如何处理数据?"
                items={items}
                wrap
                styles={{
                
            item: {
                flex: 'none',
                width: '31%',
                margin: '0.7px', // 四周加间距
                backgroundImage: `linear-gradient(137deg, #e5f4ff 0%, #efe7ff 100%)`,
                boxShadow: '0px 4px 9px 0px rgba(0, 0, 0, 0.11)',
                border: 0,
            },
            subItem: {
                background: 'rgba(255,255,255,0.45)',
                border: '1px solid #FFF',
            },
                }}
                onItemClick={(info) => {
                  const promptText = promptMap[info.data.key];
                  setInputValue(promptText);
                  // message.success(`You clicked a prompt: ${promptText}`);
                }}
            />
        </ConfigProvider>

        {/* <div style={{ color: 'grey', fontSize:'16px',padding: "5px 0px" }}>请选择数据处理方式</div> */}
        {/* <Select style={{ width: 250}}
                options={[
                  { value: 'AI直接处理（适用于对EXCEL公式不熟悉的用户）', label: 'direct' },
                  { value: 'AI间接处理（适用于对EXCEL公式较熟悉的用户）', label: 'indirect' },
                ]}
                // placeholder="折线图"
                defaultValue="折线图"
                // onChange={(value) => console.log('Selected chart type:', value)}
              /> */}
    
        <Sender 
        className={styles.sender}
        autoSize={{ minRows: 2, maxRows: 6 }}
        placeholder="请输入你希望如何处理数据，开始处理吧！"
        value={inputValue}
        onChange={(val) => setInputValue(val)}
        footer={({ components }) => {
        const { SendButton, LoadingButton } = components;
        return (
            <Flex justify="flex-end" align="center" gap={4}>
                <Select
                style={{ width: 145 }}
              showSearch
              placeholder="模型选择"
              filterOption={(input, option) =>
              (option?.label ?? '').toLowerCase().includes(input.toLowerCase())
              }
              defaultActiveFirstOption
              options={[
              { value: '1', label: 'gpt-4o' },
              { value: '2', label: 'deepseek-r1' },
              { value: '3', label: 'deepseek-v3' },
              { value: '4', label: 'baichuan2 (free)' },
              ]}
              onChange={(value) => {
                console.log("Selected model:", value);
                setSelectedModel(value); // Update the state with the selected value
              }}
              />
            <Divider type="vertical" />
              {loading ? (
              <LoadingButton type="default" />
              ) : (
              <SendButton type="primary" disabled={false} />
              )}
            </Flex>
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

export default DataProcess;

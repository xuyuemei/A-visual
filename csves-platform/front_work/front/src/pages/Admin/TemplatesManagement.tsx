import ProList from '@ant-design/pro-list';
import { ProListMetas } from '@ant-design/pro-list/lib';
import { Button, Collapse, message, Modal, Result, Tag } from 'antd';
import React, { useEffect, useRef, useState } from 'react';
import styles from './TemplatesManagement.module.css';

const TemplatesManagement: React.FC = () => {
  const [chartList, setChartList] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  /**
   * 从后端加载图表数据
   */
  const loadCharts = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/chart/list');
      const result = await response.json();
      if (response.ok) {
        setChartList(result.data || []);
      } else {
        message.error(result.message || '加载图表失败');
      }
    } catch (err) {
      console.error(err);
      message.error('加载图表失败');
    }
    setLoading(false);
  };

  useEffect(() => {
    loadCharts();
  }, []);

  const metas: ProListMetas = {
    title: {
      title: '图表名称',
      dataIndex: 'Chart_name',
    },
    subTitle: {
      title: '图表类型',
      dataIndex: 'Chart_type',
      render: (_, item) => (
        <Tag color="blue">类型：{item.Chart_type}</Tag>
      ),
    },
    content: {
      title: '图表描述',
      dataIndex: 'Chart_desc',
      render: (_, item) => (
        <div>
          <p>{item.Chart_desc}</p>
          <Collapse
            bordered={false}
            items={[
              {
                key: item.Chart_ID,
                label: '图表代码',
                children: <pre>{item.Chart_code}</pre>,
              },
            ]}
          />
        </div>
      ),
    },
  };

  return (
    <div className={styles.page}>
      <ProList
        ghost
        grid={{ gutter: 16, column: 2 }}
        loading={loading}
        rowKey="Chart_ID"
        dataSource={chartList}
        metas={metas}
        search={{
          labelWidth: 'auto',
          defaultCollapsed: false,
        }}
      />
    </div>
  );
};

export default TemplatesManagement;

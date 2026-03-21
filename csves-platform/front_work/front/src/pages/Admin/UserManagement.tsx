import React, { useState } from "react";
import { Table, Button, Dropdown, Menu, Modal, message } from "antd";
import { DownOutlined } from "@ant-design/icons";
const UserManagement = () => {
  const [selectedUser, setSelectedUser] = useState<ShowDetailsUser | null>(null);
  const [modalVisible, setModalVisible] = useState(false);

  const users = [
    {
      id: 1,
      name: "张三",
      email: "zhangsan@example.com",
      status: "已启用",
      apiLimit: 1000,
    },
    {
      id: 2,
      name: "李四",
      email: "lisi@example.com",
      status: "已封禁",
      apiLimit: 500,
    },
    // ...更多用户
  ];

  interface User {
    id: number;
    name: string;
    email: string;
    status: string;
    apiLimit: number;
  }

  type MenuKey = "enable" | "disable" | "delete" | "setLimit";

  const handleMenuClick = (key: MenuKey, user: User): void => {
    switch (key) {
      case "enable":
        message.success(`已启用 ${user.name}`);
        break;
      case "disable":
        message.warning(`已封禁 ${user.name}`);
        break;
      case "delete":
        message.error(`已删除 ${user.name}`);
        break;
      case "setLimit":
        message.info(`设置 ${user.name} 的 API 上限`);
        break;
      default:
        break;
    }
  };

  interface ShowDetailsUser {
    id: number;
    name: string;
    email: string;
    status: string;
    apiLimit: number;
  }

  const showDetails = (user: ShowDetailsUser): void => {
    setSelectedUser(user);
    setModalVisible(true);
  };

  interface ColumnRecord extends User {}

  const columns: Array<{
    title: string;
    dataIndex?: keyof ColumnRecord;
    key: string;
    render?: (_: any, record: ColumnRecord) => React.ReactNode;
  }> = [
    {
      title: "用户名",
      dataIndex: "name",
      key: "name",
    },
    {
      title: "邮箱",
      dataIndex: "email",
      key: "email",
    },
    {
      title: "状态",
      dataIndex: "status",
      key: "status",
    },
    {
      title: "API剩余次数",
      dataIndex: "apiLimit",
      key: "apiLimit",
    },
    {
      title: "操作",
      key: "action",
      render: (_: any, record: ColumnRecord) => {
        return React.createElement(
          React.Fragment,
          null,
          React.createElement(
            Dropdown,
            {
              overlay: React.createElement(Menu, {
                onClick: ({ key }) => handleMenuClick(key as MenuKey, record),
                items: [
                  { label: "启用", key: "enable" },
                  { label: "封禁", key: "disable" },
                  { label: "删除", key: "delete" },
                  { label: "设置 API 上限", key: "setLimit" },
                ],
              }),
            },
            React.createElement(
              Button,
              null,
              "操作 ",
              React.createElement(DownOutlined, null)
            )
          ),
          React.createElement(
            Button,
            { type: "link", onClick: () => showDetails(record) },
            "详情"
          )
        );
      },
    },
  ];

  return (
    <>
      <Table
        columns={columns}
        dataSource={users}
        rowKey="id"
        pagination={{ pageSize: 5 }}
        title={() => <h3>用户管理</h3>} 
      />

      <Modal
        title="用户详情"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
      >
        {selectedUser && (
          <div>
            <p><strong>用户名：</strong>{selectedUser.name}</p>
            <p><strong>邮箱：</strong>{selectedUser.email}</p>
            <p><strong>状态：</strong>{selectedUser.status}</p>
            <p><strong>API 上限：</strong>{selectedUser.apiLimit}</p>
          </div>
        )}
      </Modal>
    </>
  );
};

export default UserManagement;

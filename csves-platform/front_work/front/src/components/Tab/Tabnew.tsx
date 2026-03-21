import React, { useState } from 'react';
import styles from './Tabnew.module.css';

export interface Tab {
  key: string;
  label: string;
  content: React.ReactNode;
}

interface TabnewProps {
  tabs: Tab[];
}

export default function Tabnew({ tabs }: TabnewProps) {
  const [activeTab, setActiveTab] = useState(tabs[0]?.key || '');

  return (
    <div className={styles.container}>
      <div className={styles.buttons}>
        {tabs.map((tab) => (
          <button
            key={tab.key}
            className={activeTab === tab.key ? styles.active : styles.button}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div className={styles.content}>
        {tabs.map(
          (tab) =>
            tab.key === activeTab && (
              <div key={styles.key} className={styles.key}>
                {tab.content}
              </div>
            )
        )}
      </div>
    </div>
  );
}

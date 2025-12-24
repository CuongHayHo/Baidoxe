/**
 * Native Features Example Component
 * Demonstrates how to use Electron native features in React
 */

import React from 'react';
import useElectron from './useElectron';

export const NativeFeaturesExample: React.FC = () => {
  const { showNotification, exportData, openFile, isElectron } = useElectron();

  const handleNotification = async () => {
    await showNotification(
      '✅ Thông báo thử',
      'Đây là một thông báo từ Electron desktop app'
    );
  };

  const handleExport = async () => {
    const data = {
      timestamp: new Date().toISOString(),
      message: 'Dữ liệu export từ desktop app',
    };

    const success = await exportData(data);
    if (success) {
      await showNotification('✅ Xuất dữ liệu thành công', 'File đã được lưu');
    }
  };

  const handleOpenFile = async () => {
    const filePath = await openFile({
      filters: [
        { name: 'JSON Files', extensions: ['json'] },
        { name: 'All Files', extensions: ['*'] },
      ],
    });

    if (filePath) {
      await showNotification('📂 File đã mở', filePath);
    }
  };

  if (!isElectron) {
    return (
      <div style={{ padding: '20px', color: '#999' }}>
        Native features chỉ hoạt động trên Electron desktop app
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h3>🖥️ Native Features Demo</h3>
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        <button onClick={handleNotification} style={buttonStyle}>
          📢 Hiển thị Notification
        </button>
        <button onClick={handleExport} style={buttonStyle}>
          💾 Xuất Dữ liệu
        </button>
        <button onClick={handleOpenFile} style={buttonStyle}>
          📂 Mở File
        </button>
      </div>
    </div>
  );
};

const buttonStyle: React.CSSProperties = {
  padding: '10px 15px',
  backgroundColor: '#3498db',
  color: 'white',
  border: 'none',
  borderRadius: '4px',
  cursor: 'pointer',
  fontSize: '14px',
  fontWeight: '500',
};

export default NativeFeaturesExample;

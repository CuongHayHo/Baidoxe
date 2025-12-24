/**
 * Components index - Symlink tới các React components từ frontend
 * Desktop app sẽ sử dụng cùng components như web version
 */

// Path alias để import từ frontend components
// Sử dụng các path này thay vì hardcode paths

export { default as Dashboard } from '../../frontend/src/components/Dashboard';
export { default as CardList } from '../../frontend/src/components/CardList';
export { default as ParkingSlots } from '../../frontend/src/components/ParkingSlots';
export { default as AdminPanel } from '../../frontend/src/components/AdminPanel';
export { default as LogViewer } from '../../frontend/src/components/LogViewer';
export { default as Notifications, NotificationProvider } from '../../frontend/src/components/Notifications';
export { default as AddCardForm } from '../../frontend/src/components/AddCardForm';
export { default as UnknownCardNotification } from '../../frontend/src/components/UnknownCardNotification';

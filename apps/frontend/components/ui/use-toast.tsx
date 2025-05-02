import * as React from "react";

// Интерфейс для тостов
export interface ToastProps {
  id: string;
  title?: string;
  description?: string;
  action?: React.ReactNode;
  variant?: "default" | "success" | "error" | "warning";
}

// Создаем контекст для тостов
const ToastContext = React.createContext<{
  toasts: ToastProps[];
  addToast: (toast: Omit<ToastProps, "id">) => void;
  removeToast: (id: string) => void;
}>({
  toasts: [],
  addToast: () => {},
  removeToast: () => {},
});

// Провайдер для тостов
export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<ToastProps[]>([]);

  const addToast = React.useCallback(
    (toast: Omit<ToastProps, "id">) => {
      const id = Math.random().toString(36).substring(2, 9);
      setToasts((prev) => [...prev, { id, ...toast }]);

      // Автоматически удаляем тост через 5 секунд
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 5000);
    },
    [setToasts]
  );

  const removeToast = React.useCallback(
    (id: string) => {
      setToasts((prev) => prev.filter((toast) => toast.id !== id));
    },
    [setToasts]
  );

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <ToastContainer />
    </ToastContext.Provider>
  );
}

// Компонент для отображения тостов
function ToastContainer() {
  const { toasts, removeToast } = React.useContext(ToastContext);

  if (toasts.length === 0) return null;

  return (
    <div className="fixed bottom-0 right-0 z-50 w-full md:max-w-sm p-4 md:p-6 flex flex-col gap-2">
      {toasts.map((toast) => (
        <Toast key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
      ))}
    </div>
  );
}

// Компонент для отображения одного тоста
function Toast({
  toast,
  onClose,
}: {
  toast: ToastProps;
  onClose: () => void;
}) {
  // Определяем цвета в зависимости от варианта
  let bgColor = "bg-white";
  let borderColor = "border-gray-200";
  
  if (toast.variant === "success") {
    bgColor = "bg-green-50";
    borderColor = "border-green-200";
  } else if (toast.variant === "error") {
    bgColor = "bg-red-50";
    borderColor = "border-red-200";
  } else if (toast.variant === "warning") {
    bgColor = "bg-yellow-50";
    borderColor = "border-yellow-200";
  }

  return (
    <div
      className={`p-4 rounded-md shadow-md border ${borderColor} ${bgColor} 
                  transform transition-all duration-300 ease-in-out`}
    >
      <div className="flex justify-between items-start">
        <div>
          {toast.title && (
            <div className="font-medium">{toast.title}</div>
          )}
          {toast.description && (
            <div className="text-sm text-gray-500 mt-1">{toast.description}</div>
          )}
        </div>
        <button
          onClick={onClose}
          className="ml-4 inline-flex flex-shrink-0 justify-center items-center h-5 w-5 rounded-md text-gray-400 hover:text-gray-500"
        >
          <span className="sr-only">Закрыть</span>
          <svg 
            className="h-4 w-4" 
            fill="none" 
            viewBox="0 0 24 24" 
            stroke="currentColor"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M6 18L18 6M6 6l12 12" 
            />
          </svg>
        </button>
      </div>
      {toast.action && (
        <div className="mt-2">{toast.action}</div>
      )}
    </div>
  );
}

// Хук для использования тостов в компонентах
export function useToast() {
  const context = React.useContext(ToastContext);
  
  if (!context) {
    throw new Error("useToast must be used within ToastProvider");
  }
  
  return {
    toast: context.addToast,
    dismiss: context.removeToast,
    toasts: context.toasts,
  };
} 
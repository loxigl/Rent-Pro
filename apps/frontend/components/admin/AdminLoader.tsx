import React from 'react';

export default function AdminLoader() {
  return (
    <div className="flex items-center justify-center p-8">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
      <span className="ml-3 text-sm text-muted-foreground">Загрузка...</span>
    </div>
  );
} 
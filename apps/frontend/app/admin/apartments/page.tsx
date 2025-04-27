"use client";

import { useState } from 'react';
import ApartmentTable from '@/components/admin/apartments/ApartmentTable';

export default function AdminApartmentsPage() {
  const [refreshCounter, setRefreshCounter] = useState(0);

  // Функция для обновления списка квартир после удаления
  const handleApartmentDelete = () => {
    setRefreshCounter(prev => prev + 1);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Управление квартирами</h1>

      <ApartmentTable
        key={refreshCounter} // Это заставит компонент перерендериться при изменении счетчика
        onApartmentDelete={handleApartmentDelete}
      />
    </div>
  );
}
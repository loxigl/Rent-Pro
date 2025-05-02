'use client';

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Calendar } from "lucide-react";
import BookingForm from "./BookingForm";
import { getSystemSettings } from '@/lib/api/settings';

interface BookingButtonProps {
  apartmentId: number;
  price: number;
  bookingEnabled: boolean;
}

const BookingButton = ({ apartmentId, price, bookingEnabled }: BookingButtonProps) => {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [globalBookingEnabled, setGlobalBookingEnabled] = useState(true);
  const [loading, setLoading] = useState(true);

  // Проверяем, включена ли система бронирования глобально
  useEffect(() => {
    const checkBookingSettings = async () => {
      try {
        const settings = await getSystemSettings();
        setGlobalBookingEnabled(settings.booking_globally_enabled);
      } catch (error) {
        console.error('Ошибка при получении настроек системы:', error);
      } finally {
        setLoading(false);
      }
    };

    checkBookingSettings();
  }, []);

  const toggleForm = () => {
    setIsFormOpen(!isFormOpen);
  };

  // Если загрузка еще идет, показываем кнопку в состоянии загрузки
  if (loading) {
    return (
      <Button variant="default" className="w-full md:w-auto" disabled={true}>
        <Calendar className="mr-2 h-4 w-4" />
        Загрузка...
      </Button>
    );
  }

  // Если бронирование отключено (глобально или для конкретной квартиры)
  if (!globalBookingEnabled || !bookingEnabled) {
    return (
      <Button 
        variant="outline" 
        className="w-full md:w-auto bg-slate-100 text-slate-500" 
        disabled={true}
        title="Бронирование временно недоступно"
      >
        <Calendar className="mr-2 h-4 w-4" />
        Бронирование недоступно
      </Button>
    );
  }

  return (
    <>
      <Button 
        variant="default" 
        className="w-full md:w-auto" 
        onClick={toggleForm}
      >
        <Calendar className="mr-2 h-4 w-4" />
        Забронировать
      </Button>

      {isFormOpen && (
        <BookingForm 
          apartmentId={apartmentId} 
          price={price} 
          isOpen={isFormOpen} 
          onClose={toggleForm} 
        />
      )}
    </>
  );
};

export default BookingButton; 
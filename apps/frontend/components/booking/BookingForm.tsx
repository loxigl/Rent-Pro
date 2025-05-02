'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { CalendarIcon, X } from 'lucide-react';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { useToast } from '@/components/ui/use-toast';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { checkAvailability, createBooking } from '@/lib/api/bookings';

// Схема валидации формы бронирования
const bookingFormSchema = z.object({
  client_name: z.string().min(2, {
    message: 'Имя должно содержать не менее 2 символов',
  }),
  client_phone: z.string().min(10, {
    message: 'Введите корректный номер телефона',
  }),
  client_email: z.string().email({
    message: 'Введите корректный email',
  }).optional().or(z.literal('')),
  client_comment: z.string().optional(),
  check_in_date: z.date({
    required_error: 'Пожалуйста, выберите дату заезда',
  }),
  check_out_date: z.date({
    required_error: 'Пожалуйста, выберите дату выезда',
  }),
  guests_count: z.number().int().positive().min(1),
}).refine(data => data.check_out_date > data.check_in_date, {
  message: 'Дата выезда должна быть позже даты заезда',
  path: ['check_out_date'],
});

type BookingFormData = z.infer<typeof bookingFormSchema>;

interface BookingFormProps {
  apartmentId: number;
  isOpen: boolean;
  onClose: () => void;
  price: number;
  bookingEnabled: boolean;
}

export default function BookingForm({ apartmentId, isOpen, onClose, price, bookingEnabled }: BookingFormProps) {
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAvailabilityChecking, setIsAvailabilityChecking] = useState(false);
  const [isAvailable, setIsAvailable] = useState<boolean | null>(null);

  // Инициализация формы с react-hook-form и zod
  const form = useForm<BookingFormData>({
    resolver: zodResolver(bookingFormSchema),
    defaultValues: {
      client_name: '',
      client_phone: '',
      client_email: '',
      client_comment: '',
      guests_count: 1,
    },
  });

  // Функция для проверки доступности дат
  const checkDatesAvailability = async (checkIn: Date, checkOut: Date) => {
    if (!checkIn || !checkOut || checkOut <= checkIn) {
      return;
    }

    setIsAvailabilityChecking(true);
    try {
      const available = await checkAvailability(apartmentId, checkIn, checkOut);
      setIsAvailable(available);
      
      if (!available) {
        toast({
          title: 'Даты недоступны',
          description: 'Выбранные даты уже забронированы. Пожалуйста, выберите другие даты.',
          variant: 'destructive',
        });
      }
    } catch (error) {
      console.error('Ошибка при проверке доступности дат:', error);
      setIsAvailable(null);
    } finally {
      setIsAvailabilityChecking(false);
    }
  };

  // Обработчик отправки формы
  const onSubmit = async (data: BookingFormData) => {
    if (!bookingEnabled) {
      toast({
        title: 'Бронирование недоступно',
        description: 'В данный момент бронирование этой квартиры недоступно.',
        variant: 'destructive',
      });
      return;
    }

    // Финальная проверка доступности дат перед отправкой
    setIsSubmitting(true);
    try {
      const available = await checkAvailability(apartmentId, data.check_in_date, data.check_out_date);
      
      if (!available) {
        toast({
          title: 'Даты недоступны',
          description: 'Выбранные даты уже забронированы. Пожалуйста, выберите другие даты.',
          variant: 'destructive',
        });
        setIsSubmitting(false);
        return;
      }
      
      // Отправка данных формы
      const booking = await createBooking({
        ...data,
        apartment_id: apartmentId,
      });
      
      toast({
        title: 'Бронирование отправлено',
        description: 'Мы свяжемся с вами для подтверждения бронирования.',
        variant: 'default',
      });
      
      // Закрываем форму и сбрасываем её значения
      form.reset();
      onClose();
    } catch (error) {
      console.error('Ошибка при создании бронирования:', error);
      toast({
        title: 'Ошибка бронирования',
        description: 'Произошла ошибка при отправке запроса. Пожалуйста, попробуйте позже.',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Расчет общей стоимости проживания
  const calculateTotalPrice = () => {
    const { check_in_date, check_out_date } = form.getValues();
    if (!check_in_date || !check_out_date) return 0;
    
    const diffTime = Math.abs(check_out_date.getTime() - check_in_date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return price * diffDays;
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="relative w-full max-w-md bg-white rounded-lg p-6 shadow-lg">
        <button 
          onClick={onClose}
          className="absolute top-4 right-4 p-1 rounded-full hover:bg-gray-100"
        >
          <X className="h-5 w-5" />
        </button>
        
        <h2 className="text-xl font-bold mb-4">Забронировать квартиру</h2>
        
        {!bookingEnabled ? (
          <div className="p-4 mb-4 bg-yellow-50 border border-yellow-200 rounded-md">
            <p className="text-yellow-800">
              В данный момент бронирование этой квартиры недоступно. 
              Пожалуйста, свяжитесь с нами по телефону для получения информации.
            </p>
          </div>
        ) : null}
        
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="client_name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Ваше имя</FormLabel>
                  <FormControl>
                    <Input placeholder="Иван Иванов" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="client_phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Телефон</FormLabel>
                  <FormControl>
                    <Input placeholder="+7 (XXX) XXX-XX-XX" type="tel" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="client_email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email (необязательно)</FormLabel>
                  <FormControl>
                    <Input placeholder="example@mail.ru" type="email" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="check_in_date"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Дата заезда</FormLabel>
                    <Popover>
                      <PopoverTrigger asChild>
                        <FormControl>
                          <Button
                            variant="outline"
                            className={`w-full pl-3 text-left font-normal ${!field.value ? 'text-muted-foreground' : ''}`}
                          >
                            {field.value ? (
                              format(field.value, 'PPP', { locale: ru })
                            ) : (
                              <span>Выберите дату</span>
                            )}
                            <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                          </Button>
                        </FormControl>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={field.value}
                          onSelect={(date) => {
                            field.onChange(date);
                            const checkOut = form.getValues('check_out_date');
                            if (date && checkOut && checkOut > date) {
                              checkDatesAvailability(date, checkOut);
                            }
                          }}
                          disabled={(date) => date < new Date()}
                          locale={ru}
                        />
                      </PopoverContent>
                    </Popover>
                    <FormMessage />
                  </FormItem>
                )}
              />
              
              <FormField
                control={form.control}
                name="check_out_date"
                render={({ field }) => (
                  <FormItem className="flex flex-col">
                    <FormLabel>Дата выезда</FormLabel>
                    <Popover>
                      <PopoverTrigger asChild>
                        <FormControl>
                          <Button
                            variant="outline"
                            className={`w-full pl-3 text-left font-normal ${!field.value ? 'text-muted-foreground' : ''}`}
                          >
                            {field.value ? (
                              format(field.value, 'PPP', { locale: ru })
                            ) : (
                              <span>Выберите дату</span>
                            )}
                            <CalendarIcon className="ml-auto h-4 w-4 opacity-50" />
                          </Button>
                        </FormControl>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={field.value}
                          onSelect={(date) => {
                            field.onChange(date);
                            const checkIn = form.getValues('check_in_date');
                            if (checkIn && date && date > checkIn) {
                              checkDatesAvailability(checkIn, date);
                            }
                          }}
                          disabled={(date) => {
                            const checkIn = form.getValues('check_in_date');
                            return date < new Date() || (checkIn && date <= checkIn);
                          }}
                          locale={ru}
                        />
                      </PopoverContent>
                    </Popover>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
            
            <FormField
              control={form.control}
              name="guests_count"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Количество гостей</FormLabel>
                  <FormControl>
                    <Input 
                      type="number" 
                      min={1} 
                      {...field} 
                      onChange={(e) => field.onChange(parseInt(e.target.value) || 1)}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            <FormField
              control={form.control}
              name="client_comment"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Комментарий (необязательно)</FormLabel>
                  <FormControl>
                    <Textarea 
                      placeholder="Дополнительные пожелания или вопросы"
                      className="resize-none"
                      {...field} 
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            
            {form.getValues('check_in_date') && form.getValues('check_out_date') && (
              <div className="p-3 bg-gray-50 rounded-md">
                <p className="font-medium">Итого: {new Intl.NumberFormat('ru-RU').format(calculateTotalPrice())} ₽</p>
                <p className="text-sm text-gray-500">за весь период проживания</p>
              </div>
            )}
            
            {isAvailabilityChecking && (
              <div className="text-sm text-amber-600">
                Проверяем доступность выбранных дат...
              </div>
            )}
            
            {isAvailable === false && (
              <div className="p-3 bg-red-50 text-red-700 rounded-md text-sm">
                Выбранные даты уже забронированы. Пожалуйста, выберите другой период.
              </div>
            )}
            
            <div className="flex justify-end pt-2">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                className="mr-2"
              >
                Отмена
              </Button>
              <Button 
                type="submit" 
                disabled={isSubmitting || isAvailabilityChecking || isAvailable === false || !bookingEnabled}
              >
                {isSubmitting ? 'Отправка...' : 'Забронировать'}
              </Button>
            </div>
          </form>
        </Form>
      </div>
    </div>
  );
}
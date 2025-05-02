'use client';

import { useState } from 'react';
import { toast } from '@/components/ui/use-toast';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { 
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { X, Calendar, User, Phone, Mail, MessageSquare, Home } from 'lucide-react';
import { formatDate, formatDateFull } from '@/lib/utils/format';
import { updateBooking, updateBookingStatus } from '@/lib/api/admin/bookings';
import { BookingStatus } from '@/lib/api/types';
import { Badge } from '@/components/ui/badge';

interface BookingDetailProps {
  booking: any;  // Тип бронирования
  onClose: () => void;
  onUpdate: () => void;
}

export default function BookingDetail({ booking, onClose, onUpdate }: BookingDetailProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    client_name: booking.client_name,
    client_phone: booking.client_phone,
    client_email: booking.client_email || '',
    client_comment: booking.client_comment || '',
    admin_comment: booking.admin_comment || '',
  });

  // Обновление данных бронирования
  const handleUpdateBooking = async () => {
    setIsSubmitting(true);
    try {
      await updateBooking(booking.id, formData);
      toast({
        title: 'Данные обновлены',
        description: 'Информация о бронировании успешно обновлена',
      });
      setIsEditing(false);
      onUpdate();
    } catch (error) {
      console.error('Ошибка при обновлении бронирования:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось обновить информацию о бронировании',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Обработка изменения статуса
  const handleStatusChange = async (status: BookingStatus) => {
    try {
      await updateBookingStatus(booking.id, { 
        status, 
        admin_comment: formData.admin_comment 
      });
      toast({
        title: 'Статус обновлен',
        description: `Бронирование #${booking.id} обновлено на статус "${status}"`,
      });
      onUpdate();
    } catch (error) {
      console.error('Ошибка при обновлении статуса:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось обновить статус бронирования',
        variant: 'destructive',
      });
    }
  };

  // Обработка изменения полей формы
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Функция для отображения бейджа статуса
  const getStatusBadge = (status: BookingStatus) => {
    switch (status) {
      case 'pending':
        return <Badge variant="outline" className="bg-yellow-50 text-yellow-700 hover:bg-yellow-50">Ожидает</Badge>;
      case 'confirmed':
        return <Badge variant="outline" className="bg-green-50 text-green-700 hover:bg-green-50">Подтверждено</Badge>;
      case 'cancelled':
        return <Badge variant="outline" className="bg-red-50 text-red-700 hover:bg-red-50">Отменено</Badge>;
      case 'completed':
        return <Badge variant="outline" className="bg-blue-50 text-blue-700 hover:bg-blue-50">Завершено</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle className="flex justify-between items-center">
            <div>Бронирование #{booking.id}</div>
            <div>{getStatusBadge(booking.status)}</div>
          </DialogTitle>
          <DialogDescription>
            Создано: {formatDateFull(booking.created_at)}
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Информация о квартире */}
            <div className="space-y-4">
              <div className="flex gap-2 items-center text-slate-700">
                <Home className="h-4 w-4" />
                <span className="font-medium">Информация о квартире</span>
              </div>
              <div className="text-sm pl-6">
                <p><strong>ID квартиры:</strong> {booking.apartment_id}</p>
                {booking.apartment && (
                  <p><strong>Название:</strong> {booking.apartment.title}</p>
                )}
              </div>
              
              <div className="flex gap-2 items-center text-slate-700">
                <Calendar className="h-4 w-4" />
                <span className="font-medium">Даты проживания</span>
              </div>
              <div className="text-sm pl-6">
                <p><strong>Заезд:</strong> {formatDate(booking.check_in_date)}</p>
                <p><strong>Выезд:</strong> {formatDate(booking.check_out_date)}</p>
                <p><strong>Гостей:</strong> {booking.guests_count}</p>
              </div>
            </div>
            
            {isEditing ? (
              // Форма редактирования
              <div className="space-y-4">
                <div className="flex gap-2 items-center text-slate-700">
                  <User className="h-4 w-4" />
                  <span className="font-medium">Информация о клиенте</span>
                </div>
                
                <div className="space-y-3">
                  <div className="space-y-1">
                    <Label htmlFor="client_name">Имя</Label>
                    <Input
                      id="client_name"
                      name="client_name"
                      value={formData.client_name}
                      onChange={handleInputChange}
                    />
                  </div>
                  
                  <div className="space-y-1">
                    <Label htmlFor="client_phone">Телефон</Label>
                    <Input
                      id="client_phone"
                      name="client_phone"
                      value={formData.client_phone}
                      onChange={handleInputChange}
                    />
                  </div>
                  
                  <div className="space-y-1">
                    <Label htmlFor="client_email">Email</Label>
                    <Input
                      id="client_email"
                      name="client_email"
                      value={formData.client_email}
                      onChange={handleInputChange}
                    />
                  </div>
                </div>
              </div>
            ) : (
              // Отображение информации о клиенте
              <div className="space-y-4">
                <div className="flex gap-2 items-center text-slate-700">
                  <User className="h-4 w-4" />
                  <span className="font-medium">Информация о клиенте</span>
                </div>
                <div className="text-sm pl-6 space-y-1">
                  <div className="flex gap-2 items-center">
                    <User className="h-3 w-3 text-slate-500" />
                    <span>{booking.client_name}</span>
                  </div>
                  <div className="flex gap-2 items-center">
                    <Phone className="h-3 w-3 text-slate-500" />
                    <span>{booking.client_phone}</span>
                  </div>
                  {booking.client_email && (
                    <div className="flex gap-2 items-center">
                      <Mail className="h-3 w-3 text-slate-500" />
                      <span>{booking.client_email}</span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
          
          {/* Комментарии */}
          <div className="space-y-4 mt-4">
            <div className="flex gap-2 items-center text-slate-700">
              <MessageSquare className="h-4 w-4" />
              <span className="font-medium">Комментарии</span>
            </div>
            
            {isEditing ? (
              <div className="space-y-3">
                <div className="space-y-1">
                  <Label htmlFor="client_comment">Комментарий клиента</Label>
                  <Textarea
                    id="client_comment"
                    name="client_comment"
                    value={formData.client_comment}
                    onChange={handleInputChange}
                    rows={3}
                  />
                </div>
                
                <div className="space-y-1">
                  <Label htmlFor="admin_comment">Комментарий администратора</Label>
                  <Textarea
                    id="admin_comment"
                    name="admin_comment"
                    value={formData.admin_comment}
                    onChange={handleInputChange}
                    rows={3}
                  />
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-3">
                <div>
                  <h4 className="text-sm font-medium mb-1">Комментарий клиента:</h4>
                  <p className="text-sm text-slate-600 pl-3 border-l-2 border-slate-200">
                    {booking.client_comment || "Нет комментария"}
                  </p>
                </div>
                
                <div>
                  <h4 className="text-sm font-medium mb-1">Комментарий администратора:</h4>
                  <p className="text-sm text-slate-600 pl-3 border-l-2 border-slate-200">
                    {booking.admin_comment || "Нет комментария"}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
        
        <DialogFooter className="flex flex-col sm:flex-row gap-2">
          {isEditing ? (
            <>
              <Button
                variant="outline"
                onClick={() => setIsEditing(false)}
              >
                Отмена
              </Button>
              <Button
                onClick={handleUpdateBooking}
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Сохранение...' : 'Сохранить изменения'}
              </Button>
            </>
          ) : (
            <>
              <div className="flex gap-2 flex-wrap justify-end">
                <Button
                  variant="outline"
                  onClick={() => setIsEditing(true)}
                >
                  Редактировать
                </Button>
                
                <div className="space-x-2">
                  {booking.status !== 'confirmed' && (
                    <Button
                      variant="default"
                      className="bg-green-600 hover:bg-green-700"
                      onClick={() => handleStatusChange('confirmed')}
                    >
                      Подтвердить
                    </Button>
                  )}
                  
                  {booking.status !== 'cancelled' && (
                    <Button
                      variant="destructive"
                      onClick={() => handleStatusChange('cancelled')}
                    >
                      Отменить
                    </Button>
                  )}
                  
                  {booking.status !== 'completed' && booking.status !== 'cancelled' && (
                    <Button
                      variant="default"
                      className="bg-blue-600 hover:bg-blue-700"
                      onClick={() => handleStatusChange('completed')}
                    >
                      Завершить
                    </Button>
                  )}
                </div>
              </div>
            </>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
} 
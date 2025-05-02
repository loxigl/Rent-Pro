'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { BookingStatus } from '@/lib/api/types';
import {
  getBookings,
  updateBookingStatus,
  deleteBooking
} from '@/lib/api/admin/bookings';
import { useToast } from '@/components/ui/use-toast';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious
} from '@/components/ui/pagination';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { Badge } from '@/components/ui/badge';
import { formatDate } from '@/lib/utils/format';
import AdminHeader from '@/components/admin/AdminHeader';
import AdminLoader from '@/components/admin/AdminLoader';
import BookingDetail from '@/components/admin/bookings/BookingDetail';

export default function BookingsClient() {
  const { toast } = useToast();
  const searchParams = useSearchParams();

  // Состояние
  const [bookings, setBookings] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState<BookingStatus | "">("");
  const [filterName, setFilterName] = useState("");
  const [selectedBooking, setSelectedBooking] = useState<any | null>(null);
  const [bookingToDelete, setBookingToDelete] = useState<number | null>(null);

  // Получение бронирований с учетом фильтров
  const fetchBookings = async () => {
    setLoading(true);
    try {
      const response = await getBookings({
        page,
        limit: 10,
        status: filterStatus || undefined,
        client_name: filterName || undefined
      });

      setBookings(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Ошибка при загрузке бронирований:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось загрузить список бронирований',
        variant: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  // Загрузка бронирований при изменении фильтров или страницы
  useEffect(() => {
    fetchBookings();
  }, [page, filterStatus, filterName]);

  // Обработчик изменения статуса бронирования
  const handleStatusChange = async (bookingId: number, status: BookingStatus) => {
    try {
      await updateBookingStatus(bookingId, { status });
      toast({
        title: 'Статус обновлен',
        description: `Бронирование #${bookingId} обновлено на статус "${status}"`,
      });

      // Обновляем список
      fetchBookings();

      // Обновляем детали если открыты
      if (selectedBooking && selectedBooking.id === bookingId) {
        setSelectedBooking({
          ...selectedBooking,
          status
        });
      }
    } catch (error) {
      console.error('Ошибка при обновлении статуса:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось обновить статус бронирования',
        variant: 'error',
      });
    }
  };

  // Обработчик удаления бронирования
  const handleDelete = async () => {
    if (!bookingToDelete) return;

    try {
      await deleteBooking(bookingToDelete);
      toast({
        title: 'Бронирование удалено',
        description: `Бронирование #${bookingToDelete} успешно удалено`,
      });

      // Закрываем детали если открыты
      if (selectedBooking && selectedBooking.id === bookingToDelete) {
        setSelectedBooking(null);
      }

      // Обновляем список
      fetchBookings();

      // Сбрасываем ID
      setBookingToDelete(null);
    } catch (error) {
      console.error('Ошибка при удалении бронирования:', error);
      toast({
        title: 'Ошибка',
        description: 'Не удалось удалить бронирование',
        variant: 'error',
      });
    }
  };

  // Функция для получения цвета бейджа в зависимости от статуса
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

  // Расчет общего количества страниц
  const totalPages = Math.ceil(total / 10);

  return (
    <div className="container mx-auto py-6">
      <AdminHeader
        title="Управление бронированиями"
        description="Просмотр и управление бронированиями квартир"
      />

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-6">
        {/* Сайдбар с фильтрами */}
        <div className="md:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Фильтры</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium" htmlFor="status-filter">
                  Статус
                </label>
                <Select
                  value={filterStatus}
                  onValueChange={(value) => {
                    setFilterStatus(value as BookingStatus | "");
                    setPage(1);
                  }}
                >
                  <SelectTrigger id="status-filter">
                    <SelectValue placeholder="Все статусы" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">Все статусы</SelectItem>
                    <SelectItem value="pending">Ожидает</SelectItem>
                    <SelectItem value="confirmed">Подтверждено</SelectItem>
                    <SelectItem value="cancelled">Отменено</SelectItem>
                    <SelectItem value="completed">Завершено</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium" htmlFor="name-filter">
                  Имя клиента
                </label>
                <Input
                  id="name-filter"
                  placeholder="Поиск по имени"
                  value={filterName}
                  onChange={(e) => setFilterName(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      setPage(1);
                      fetchBookings();
                    }
                  }}
                />
                <Button
                  variant="outline"
                  className="w-full mt-2"
                  onClick={() => {
                    setPage(1);
                    fetchBookings();
                  }}
                >
                  Применить
                </Button>
              </div>

              <Button
                variant="ghost"
                className="w-full mt-4"
                onClick={() => {
                  setFilterStatus("");
                  setFilterName("");
                  setPage(1);
                }}
              >
                Сбросить фильтры
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Список бронирований */}
        <div className="md:col-span-3">
          <Card>
            <CardHeader>
              <div className="flex justify-between">
                <CardTitle>Список бронирований</CardTitle>
                <span className="text-sm text-gray-500">
                  Всего: {total}
                </span>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="flex justify-center py-8">
                  <AdminLoader />
                </div>
              ) : bookings.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  Бронирования не найдены
                </div>
              ) : (
                <>
                  <Table>
                    <TableCaption>Список всех бронирований</TableCaption>
                    <TableHeader>
                      <TableRow>
                        <TableHead className="w-[80px]">ID</TableHead>
                        <TableHead>Клиент</TableHead>
                        <TableHead>Даты</TableHead>
                        <TableHead>Статус</TableHead>
                        <TableHead>Действия</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {bookings.map((booking) => (
                        <TableRow key={booking.id}>
                          <TableCell className="font-medium">
                            {booking.id}
                          </TableCell>
                          <TableCell>
                            <div>
                              <div className="font-medium">{booking.client_name}</div>
                              <div className="text-sm text-gray-500">{booking.client_phone}</div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="text-sm">
                              <div>С: {formatDate(booking.check_in_date)}</div>
                              <div>По: {formatDate(booking.check_out_date)}</div>
                            </div>
                          </TableCell>
                          <TableCell>
                            {getStatusBadge(booking.status)}
                          </TableCell>
                          <TableCell>
                            <div className="flex space-x-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setSelectedBooking(booking)}
                              >
                                Детали
                              </Button>

                              <Select
                                defaultValue={booking.status}
                                onValueChange={(value) => handleStatusChange(booking.id, value as BookingStatus)}
                              >
                                <SelectTrigger className="w-[130px]">
                                  <SelectValue placeholder="Изменить статус" />
                                </SelectTrigger>
                                <SelectContent>
                                  <SelectItem value="pending">Ожидает</SelectItem>
                                  <SelectItem value="confirmed">Подтвердить</SelectItem>
                                  <SelectItem value="cancelled">Отменить</SelectItem>
                                  <SelectItem value="completed">Завершить</SelectItem>
                                </SelectContent>
                              </Select>

                              <AlertDialog>
                                <AlertDialogTrigger asChild>
                                  <Button
                                    variant="destructive"
                                    size="sm"
                                    onClick={() => setBookingToDelete(booking.id)}
                                  >
                                    Удалить
                                  </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                  <AlertDialogHeader>
                                    <AlertDialogTitle>Удаление бронирования</AlertDialogTitle>
                                    <AlertDialogDescription>
                                      Вы уверены, что хотите удалить бронирование #{booking.id}?
                                      Это действие невозможно отменить.
                                    </AlertDialogDescription>
                                  </AlertDialogHeader>
                                  <AlertDialogFooter>
                                    <AlertDialogCancel onClick={() => setBookingToDelete(null)}>
                                      Отмена
                                    </AlertDialogCancel>
                                    <AlertDialogAction onClick={handleDelete}>
                                      Удалить
                                    </AlertDialogAction>
                                  </AlertDialogFooter>
                                </AlertDialogContent>
                              </AlertDialog>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>

                  {/* Пагинация */}
                  {totalPages > 1 && (
                    <Pagination className="mt-4">
                      <PaginationContent>
                        <PaginationItem>
                          <PaginationPrevious
                            href='#'
                            onClick={() => setPage(prev => Math.max(prev - 1, 1))}
                            isActive={page > 1}
                          />
                        </PaginationItem>

                        {Array.from({ length: Math.min(totalPages, 5) }, (_, i) => {
                          const pageNum = i + 1 + Math.max(0, page - 3);
                          if (pageNum > totalPages) return null;

                          return (
                            <PaginationItem key={pageNum}>
                              <PaginationLink
                                href='#'
                                isActive={page === pageNum}
                                onClick={() => setPage(pageNum)}
                              >
                                {pageNum}
                              </PaginationLink>
                            </PaginationItem>
                          );
                        })}

                        <PaginationItem>
                          <PaginationNext
                            href='#'
                            onClick={() => setPage(prev => Math.min(prev + 1, totalPages))}
                            isActive={page < totalPages}
                          />
                        </PaginationItem>
                      </PaginationContent>
                    </Pagination>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Модальное окно с деталями бронирования */}
      {selectedBooking && (
        <BookingDetail
          booking={selectedBooking}
          onClose={() => setSelectedBooking(null)}
          onUpdate={fetchBookings}
        />
      )}
    </div>
  );
} 
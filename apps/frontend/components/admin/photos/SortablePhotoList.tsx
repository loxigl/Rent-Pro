"use client";
import {cn} from "@/lib/utils/cn";
import {useState, useEffect} from 'react';
import Image from 'next/image';
import {Button} from '@/components/ui/Button';

// Интерфейс для фотографии
interface Photo {
    id: number;
    url: string;
    thumbnail_url?: string;
    apartment_id: number;
    sort_order: number;
    is_cover: boolean;
    created_at: string;
    processing_status?: "pending" | "completed" | "failed";
    local_preview?: string;

}

interface SortablePhotoListProps {
    photos: Photo[];
    onReorder?: (reorderedPhotos: Photo[]) => void;
    onSetCover?: (photoId: number) => void;
    onDeletePhoto?: (photoId: number) => void;
    isSaving?: boolean;
}


export default function SortablePhotoList({
                                              photos,
                                              onReorder,
                                              onSetCover,
                                              onDeletePhoto,
                                              isSaving = false
                                          }: SortablePhotoListProps) {
    const [items, setItems] = useState<Photo[]>([]);
    const [draggedItem, setDraggedItem] = useState<Photo | null>(null);
    const [hasChanges, setHasChanges] = useState(false);

    // Инициализируем состояние при изменении входных данных
    useEffect(() => {
        setItems([...photos].sort((a, b) => a.sort_order - b.sort_order));
        setHasChanges(false);
    }, [photos]);

    // Обработчик начала перетаскивания
    const handleDragStart = (e: React.DragEvent<HTMLDivElement>, item: Photo) => {
        setDraggedItem(item);
        // Для стилизации перетаскиваемого элемента (прозрачность)
        e.currentTarget.style.opacity = '0.4';
    };

    // Обработчик завершения перетаскивания
    const handleDragEnd = (e: React.DragEvent<HTMLDivElement>) => {
        e.currentTarget.style.opacity = '1';
        setDraggedItem(null);
    };

    // Обработчик наведения при перетаскивании
    const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    };

    // Обработчик сброса (drop)
    const handleDrop = (e: React.DragEvent<HTMLDivElement>, targetItem: Photo) => {
        e.preventDefault();

        if (!draggedItem || draggedItem.id === targetItem.id) {
            return;
        }

        // Создаем копию массива фотографий
        const newItems = [...items];

        // Находим индексы перетаскиваемого и целевого элементов
        const draggedIndex = newItems.findIndex(item => item.id === draggedItem.id);
        const targetIndex = newItems.findIndex(item => item.id === targetItem.id);

        // Перемещаем элемент
        const [movedItem] = newItems.splice(draggedIndex, 1);
        newItems.splice(targetIndex, 0, movedItem);

        // Обновляем порядок сортировки
        const reorderedItems = newItems.map((item, index) => ({
            ...item,
            sort_order: index
        }));

        // Обновляем состояние
        setItems(reorderedItems);
        setHasChanges(true);
    };

    // Обработчик сохранения изменений
    const handleSaveOrder = () => {
        if (onReorder) {
            onReorder(items);
            setHasChanges(false);
        }
    };

    // Форматирование даты
    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric'
        });
    };

    function photoSrc(p: Photo): string {
        // local_preview есть ТОЛЬКО пока статус pending
        if (p.processing_status === "pending") {
            return p.local_preview || ''; // Добавляем проверку на undefined
        }
        return p.thumbnail_url || p.url || ''; // Гарантируем возврат строки
    }

    return (
        <div>
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium">Фотографии ({photos.length})</h3>

                {hasChanges && (
                    <Button
                        onClick={handleSaveOrder}
                        disabled={isSaving}
                        size="sm"
                    >
                        {isSaving ? 'Сохранение...' : 'Сохранить порядок'}
                    </Button>
                )}
            </div>


            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {items.map(photo => (
                    <div
                        key={photo.id}
                        className="group relative border rounded-md overflow-hidden cursor-move transition-shadow hover:shadow-md"
                        draggable
                        onDragStart={e => handleDragStart(e, photo)}
                        onDragEnd={handleDragEnd}
                        onDragOver={handleDragOver}
                        onDrop={e => handleDrop(e, photo)}
                    >
                        <div className="relative aspect-square">
                            {/* если pending — <img>, иначе Next <Image> */}
                            {photo.processing_status === "pending" ? (
                                <img
                                    src={photoSrc(photo)}
                                    alt={`Фото ${photo.id}`}
                                    className="w-full h-full object-cover opacity-50 blur-sm
                 transition-opacity duration-300"
                                />
                            ) : (
                                <Image
                                    src={photoSrc(photo)}
                                    alt={`Фото ${photo.id}`}
                                    fill
                                    sizes="(max-width: 640px) 100vw,
             (max-width: 768px) 50vw,
             (max-width: 1024px) 33vw,
             25vw"
                                    className="object-cover transition-opacity duration-300"
                                    // если используете Next ≤13, добавьте unoptimized для внешних URL
                                    // unoptimized
                                />
                            )}

                            {/* крутилка поверх pending-фото */}
                            {photo.processing_status === "pending" && (
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <svg
                                        className="h-6 w-6 animate-spin text-white drop-shadow"
                                        viewBox="0 0 24 24"
                                    >
                                        <circle
                                            className="opacity-25"
                                            cx="12"
                                            cy="12"
                                            r="10"
                                            stroke="currentColor"
                                            strokeWidth="4"
                                        />
                                        <path
                                            className="opacity-75"
                                            fill="currentColor"
                                            d="M4 12a8 8 0 018-8V0C5.37 0 0 5.37 0 12h4z"
                                        />
                                    </svg>
                                </div>
                            )}

                            {/* Порядковый номер */}
                            <div
                                className="absolute top-2 left-2 bg-black/50 text-white rounded-full
               w-6 h-6 flex items-center justify-center text-xs"
                            >
                                {photo.sort_order + 1}
                            </div>

                            {/* Индикатор обложки */}
                            {photo.is_cover && (
                                <div className="absolute top-2 right-2 bg-primary-600 text-white
                    text-xs px-2 py-1 rounded-md">
                                    Обложка
                                </div>
                            )}
                        </div>

                        {/* Панель действий (появляется при наведении) */}
                        <div
                            className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                            <div className="flex space-x-2">
                                {/* Кнопка установки обложки */}
                                {!photo.is_cover && onSetCover && (
                                    <button
                                        onClick={() => onSetCover(photo.id)}
                                        disabled={isSaving}
                                        className="p-2 bg-white rounded-full text-primary-600 hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-primary-500"
                                        title="Сделать обложкой"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20"
                                             fill="currentColor">
                                            <path
                                                d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                                        </svg>
                                    </button>
                                )}

                                {/* Кнопка удаления */}
                                {onDeletePhoto && (
                                    <button
                                        onClick={() => onDeletePhoto(photo.id)}
                                        disabled={isSaving}
                                        className="p-2 bg-white rounded-full text-red-600 hover:bg-red-50 focus:outline-none focus:ring-2 focus:ring-red-500"
                                        title="Удалить фото"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20"
                                             fill="currentColor">
                                            <path fillRule="evenodd"
                                                  d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z"
                                                  clipRule="evenodd"/>
                                        </svg>
                                    </button>
                                )}
                            </div>
                        </div>

                        {/* Информация о фото (дата добавления) */}
                        <div className="p-2 text-xs text-gray-500">
                            Добавлено: {formatDate(photo.created_at)}
                        </div>
                    </div>
                ))}
            </div>

            {/* Инструкции по перетаскиванию */}
            <p className="text-sm text-gray-500 mt-4">
                Перетащите фотографии, чтобы изменить порядок их отображения. Первая фотография будет показываться в
                каталоге.
            </p>
        </div>
    );
}
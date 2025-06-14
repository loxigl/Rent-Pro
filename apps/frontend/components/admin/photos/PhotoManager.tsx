"use client";

import {useState, useEffect} from 'react';
import PhotoUploader from '@/components/admin/photos/PhotoUploader';
import SortablePhotoList from '@/components/admin/photos/SortablePhotoList';
import {Button} from '@/components/ui/button';
import {getAccessToken} from '@/lib/utils/admin/jwt';
import {getApiBaseUrl} from "@/lib/api/config";

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

// Интерфейс для ответа API с фотографиями
interface PhotoListResponse {
    items: Photo[];
    total: number;
}

interface PhotoManagerProps {
    apartmentId: number;
}

export const API_URL = getApiBaseUrl();

export default function PhotoManager({apartmentId}: PhotoManagerProps) {
    const [photos, setPhotos] = useState<Photo[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isSaving, setIsSaving] = useState(false);
    const [uploadSuccess, setUploadSuccess] = useState(false);

    // Загружаем список фотографий
    const fetchPhotos = async () => {
        try {
            setIsLoading(true);
            setError(null);

            // Получаем токен доступа
            const token = await getAccessToken();

            // Выполняем запрос
            const response = await fetch(`${API_URL}/admin/api/v1/photos/${apartmentId}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`Ошибка загрузки фотографий: ${response.status}`);
            }

            const data: PhotoListResponse = await response.json();
            const mapped: Photo[] = data.items.map(p => ({
                ...p,
                processing_status:
                // берём из метаданных, либо считаем завершённым
                    ((p as any).photo_metadata?.processing_status as
                        | "pending"
                        | "completed"
                        | "failed") ?? "completed",
            }));

            setPhotos(prev =>
                mapped.map(p => {
                    const old = prev.find(o => o.id === p.id);
                    return p.processing_status === "completed"
                        ? p                           // готово → превью больше не нужно
                        : {...p, local_preview: old?.local_preview};
                }),
            );
        } catch (err: any) {
            setError(err.message || 'Произошла ошибка при загрузке фотографий');
            console.error('Ошибка при загрузке фотографий:', err);
        } finally {
            setIsLoading(false);
        }
    };

    // Загружаем фотографии при монтировании компонента и при изменении ID квартиры
    useEffect(() => {
        if (apartmentId) {
            fetchPhotos();
        }
    }, [apartmentId]);

    useEffect(() => {
        const hasPending = photos.some(p => p.processing_status === "pending");
        if (!hasPending) return;

        const id = setInterval(fetchPhotos, 3000);   // опрашиваем каждые 3 с
        return () => clearInterval(id);
    }, [photos]);   // ← перезапуск, когда список меняется


    const handlePhotoUploaded = (photo: Photo & { local_preview: string }) => {
        setUploadSuccess(true);
        setTimeout(() => setUploadSuccess(false), 3000);

        setPhotos(prev => [
            ...prev,
            {
                ...photo,
                processing_status: "pending",
            },
        ]);
    };

    // Обработчик изменения порядка фотографий
    const handleReorder = async (reorderedPhotos: Photo[]) => {
        try {
            setIsSaving(true);

            // Получаем токен доступа
            const token = await getAccessToken();

            // Подготавливаем данные для запроса
            const updateData = {
                updates: reorderedPhotos.map((photo, index) => ({
                    id: photo.id,
                    sort_order: index
                }))
            };

            // Выполняем запрос
            const response = await fetch(`${API_URL}/admin/api/v1/photos/bulk-update`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(updateData)
            });

            if (!response.ok) {
                throw new Error(`Ошибка обновления порядка фотографий: ${response.status}`);
            }

            // Обновляем состояние списка фотографий
            setPhotos(reorderedPhotos.map((photo, index) => ({
                ...photo,
                sort_order: index
            })));
        } catch (err: any) {
            setError(err.message || 'Произошла ошибка при обновлении порядка фотографий');
            console.error('Ошибка при обновлении порядка фотографий:', err);
        } finally {
            setIsSaving(false);
        }
    };

    // Обработчик установки фотографии в качестве обложки
    const handleSetCover = async (photoId: number) => {
        try {
            setIsSaving(true);

            // Получаем токен доступа
            const token = await getAccessToken();

            // Выполняем запрос
            const response = await fetch(`${API_URL}/admin/api/v1/photos/${photoId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    is_cover: true
                })
            });

            if (!response.ok) {
                throw new Error(`Ошибка установки обложки: ${response.status}`);
            }

            // Обновляем состояние списка фотографий
            setPhotos(photos.map(photo => ({
                ...photo,
                is_cover: photo.id === photoId
            })));
        } catch (err: any) {
            setError(err.message || 'Произошла ошибка при установке обложки');
            console.error('Ошибка при установке обложки:', err);
        } finally {
            setIsSaving(false);
        }
    };

    // Обработчик удаления фотографии
    const handleDeletePhoto = async (photoId: number) => {
        if (!window.confirm('Вы уверены, что хотите удалить эту фотографию?')) {
            return;
        }

        try {
            setIsSaving(true);

            // Получаем токен доступа
            const token = await getAccessToken();

            // Выполняем запрос
            const response = await fetch(`${API_URL}/admin/api/v1/photos/${photoId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`Ошибка удаления фотографии: ${response.status}`);
            }

            // Удаляем фотографию из списка
            setPhotos(photos.filter(photo => photo.id !== photoId));
        } catch (err: any) {
            setError(err.message || 'Произошла ошибка при удалении фотографии');
            console.error('Ошибка при удалении фотографии:', err);
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="bg-white shadow rounded-lg overflow-hidden">
            <div className="p-6">
                <h2 className="text-lg font-semibold mb-6">Управление фотографиями</h2>

                {/* Сообщение об ошибке */}
                {error && (
                    <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-md">
                        {error}
                        <Button
                            variant="link"
                            size="sm"
                            onClick={() => {
                                setError(null);
                                fetchPhotos();
                            }}
                            className="ml-2"
                        >
                            Повторить
                        </Button>
                    </div>
                )}

                {/* Сообщение об успешной загрузке */}
                {uploadSuccess && (
                    <div className="mb-6 p-4 bg-green-50 text-green-700 rounded-md">
                        Фотография успешно загружена
                    </div>
                )}

                {/* Компонент для загрузки фотографий */}
                <div className="mb-8">
                    <PhotoUploader
                        apartmentId={apartmentId}
                        onPhotoUploaded={handlePhotoUploaded}
                    />
                </div>

                {/* Список фотографий с возможностью сортировки */}
                {isLoading ? (
                    <div className="animate-pulse space-y-4">
                        <div className="h-6 bg-gray-200 rounded"></div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                            {[1, 2, 3, 4].map(i => (
                                <div key={i} className="aspect-square bg-gray-200 rounded"></div>
                            ))}
                        </div>
                    </div>
                ) : photos.length > 0 ? (
                    <SortablePhotoList
                        photos={photos}
                        onReorder={handleReorder}
                        onSetCover={handleSetCover}
                        onDeletePhoto={handleDeletePhoto}
                        isSaving={isSaving}
                    />
                ) : (
                    <div className="text-center py-8 text-gray-500">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            className="h-12 w-12 mx-auto mb-4 text-gray-400"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                            />
                        </svg>
                        <p>У этой квартиры пока нет фотографий</p>
                        <p className="text-sm mt-2">Загрузите фотографии, чтобы они отображались в каталоге</p>
                    </div>
                )}
            </div>
        </div>
    );
}
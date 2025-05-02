"use client";

import {useState, useRef} from 'react';
import {Button} from '@/components/ui/button';
import {getAccessToken} from '@/lib/utils/admin/jwt';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Интерфейс для загруженной фотографии
interface UploadedPhoto {
    id: number;
    url: string;
    thumbnail_url?: string;
    apartment_id: number;
    sort_order: number;
    is_cover: boolean;
    created_at: string;
}

interface PhotoUploaderProps {
    apartmentId: number;
    onPhotoUploaded?: (photo: {
        id: number;
        url: string;
        thumbnail_url?: string;
        apartment_id: number;
        sort_order: number;
        is_cover: boolean;
        created_at: string;
        processing_status?: "pending" | "completed" | "failed";
        local_preview: string
    }) => void;
}

export default function PhotoUploader({apartmentId, onPhotoUploaded}: PhotoUploaderProps) {
    const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
    const [previewUrls, setPreviewUrls] = useState<string[]>([]);
    const [isUploading, setIsUploading] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Максимальный размер файла (10 МБ)
    const MAX_FILE_SIZE = 10 * 1024 * 1024;
    // Допустимые типы файлов
    const ACCEPTED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

    // Обработчик выбора файлов
    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        setError(null);

        if (!e.target.files || e.target.files.length === 0) {
            return;
        }

        const files = Array.from(e.target.files);

        // Проверяем размер и тип файлов
        const validFiles = files.filter(file => {
            if (file.size > MAX_FILE_SIZE) {
                setError(`Файл "${file.name}" слишком большой. Максимальный размер: 10 МБ`);
                return false;
            }

            if (!ACCEPTED_FILE_TYPES.includes(file.type)) {
                setError(`Файл "${file.name}" имеет недопустимый формат. Допустимые форматы: JPEG, PNG, WebP`);
                return false;
            }

            return true;
        });

        if (validFiles.length === 0) {
            return;
        }

        // Устанавливаем выбранные файлы
        setSelectedFiles(validFiles);

        // Создаем превью для выбранных файлов
        const urls = validFiles.map(file => URL.createObjectURL(file));
        setPreviewUrls(urls);
    };

    // Обработчик сброса выбранных файлов
    const handleReset = () => {
        setSelectedFiles([]);
        setPreviewUrls([]);
        setError(null);
        setUploadProgress(0);

        // Очищаем input, чтобы можно было выбрать те же файлы снова
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    // Обработчик загрузки файлов
    const handleUpload = async () => {
        if (selectedFiles.length === 0) {
            return;
        }

        setIsUploading(true);
        setUploadProgress(0);
        setError(null);

        try {
            // Получаем токен доступа
            const token = await getAccessToken();

            // Загружаем файлы последовательно
            for (let i = 0; i < selectedFiles.length; i++) {
                // Устанавливаем прогресс загрузки
                setUploadProgress(Math.round((i / selectedFiles.length) * 100));

                const file = selectedFiles[i];

                // Создаем FormData для загрузки файла
                const formData = new FormData();
                formData.append('file', file);
                formData.append('apartment_id', apartmentId.toString());

                // Выполняем запрос
                const response = await fetch(`${API_URL}/admin/api/v1/photos/` + apartmentId + '/upload', {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`
                    },
                    body: formData
                });

                if (!response.ok) {
                    throw new Error(`Ошибка загрузки файла "${file.name}": ${response.status}`);
                }

                // Получаем данные загруженной фотографии
                const data: UploadedPhoto = await response.json();

                // Вызываем колбэк для обновления списка фотографий
                onPhotoUploaded?.({
                    ...data,
                    processing_status: "pending" as const,
                    local_preview: previewUrls[i]          // <<< добавили
                });
            }

            // Устанавливаем прогресс в 100%
            setUploadProgress(100);

            // Сбрасываем выбранные файлы
            handleReset();
        } catch (err: any) {
            setError(err.message || 'Произошла ошибка при загрузке файлов');
            console.error('Ошибка при загрузке файлов:', err);
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6">
            <input
                type="file"
                ref={fileInputRef}
                accept="image/jpeg,image/png,image/webp"
                multiple
                onChange={handleFileSelect}
                className="hidden"
                disabled={isUploading}
            />

            {/* Сообщение об ошибке */}
            {error && (
                <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md text-sm">
                    {error}
                </div>
            )}

            {/* Превью выбранных файлов */}
            {previewUrls.length > 0 ? (
                <div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 mb-4">
                        {previewUrls.map((url, index) => (
                            <div key={index}
                                 className="relative aspect-square rounded-md overflow-hidden border border-gray-200">
                                <img
                                    src={url}
                                    alt={`Preview ${index}`}
                                    className="w-full h-full object-cover"
                                />
                            </div>
                        ))}
                    </div>

                    {/* Прогресс загрузки */}
                    {isUploading && (
                        <div className="mb-4">
                            <div className="h-2 bg-gray-200 rounded-full">
                                <div
                                    className="h-2 bg-primary-600 rounded-full"
                                    style={{width: `${uploadProgress}%`}}
                                ></div>
                            </div>
                            <p className="text-sm text-gray-500 mt-1">
                                Загрузка: {uploadProgress}%
                            </p>
                        </div>
                    )}

                    {/* Кнопки действий */}
                    <div className="flex justify-end space-x-3">
                        <Button
                            variant="secondary"
                            size="sm"
                            onClick={handleReset}
                            disabled={isUploading}
                        >
                            Отменить
                        </Button>
                        <Button
                            size="sm"
                            onClick={handleUpload}
                            disabled={isUploading}
                        >
                            {isUploading ? 'Загрузка...' : 'Загрузить'}
                        </Button>
                    </div>
                </div>
            ) : (
                <div
                    className="text-center cursor-pointer py-8"
                    onClick={() => fileInputRef.current?.click()}
                >
                    <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-12 w-12 mx-auto text-gray-400 mb-3"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                        />
                    </svg>
                    <h3 className="text-lg font-medium text-gray-900 mb-1">
                        Перетащите фотографии сюда
                    </h3>
                    <p className="text-sm text-gray-500">
                        или{' '}
                        <span className="text-primary-600 font-medium">выберите файлы</span>{' '}
                        для загрузки
                    </p>
                    <p className="text-xs text-gray-500 mt-2">
                        Поддерживаемые форматы: JPEG, PNG, WebP. Максимальный размер: 10 МБ.
                    </p>
                </div>
            )}
        </div>
    );
}
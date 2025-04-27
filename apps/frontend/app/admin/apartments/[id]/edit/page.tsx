"use client";

import {useState} from 'react';
import Link from 'next/link';
import {useRouter} from 'next/navigation';
import ApartmentForm from '@/components/admin/apartments/ApartmentForm';
import PhotoManager from '@/components/admin/photos/PhotoManager';

interface EditApartmentPageProps {
    params: {
        id: string;
    };
}

export default function EditApartmentPage({params}: EditApartmentPageProps) {
    const router = useRouter();
    const apartmentId = parseInt(params.id, 10);
    const [activeTab, setActiveTab] = useState<'info' | 'photos'>('info');

    // Проверяем, что ID валиден
    if (isNaN(apartmentId) || apartmentId <= 0) {
        router.push('/admin/apartments');
        return null;
    }

    return (
        <div>
            <div className="flex items-center mb-6">
                <Link href="/admin/apartments" className="text-primary-600 hover:text-primary-700 mr-2">
                    &larr; Назад к списку
                </Link>
                <h1 className="text-2xl font-bold">Редактирование квартиры #{apartmentId}</h1>
            </div>

            {/* Вкладки */}
            <div className="bg-white shadow rounded-lg overflow-hidden mb-6">
                <div className="flex border-b">
                    <button
                        className={`px-6 py-3 text-sm font-medium ${
                            activeTab === 'info'
                                ? 'text-primary-600 border-b-2 border-primary-600'
                                : 'text-gray-500 hover:text-gray-700'
                        }`}
                        onClick={() => setActiveTab('info')}
                    >
                        Основная информация
                    </button>
                    <button
                        className={`px-6 py-3 text-sm font-medium ${
                            activeTab === 'photos'
                                ? 'text-primary-600 border-b-2 border-primary-600'
                                : 'text-gray-500 hover:text-gray-700'
                        }`}
                        onClick={() => setActiveTab('photos')}
                    >
                        Фотографии
                    </button>
                </div>
            </div>

            {/* Контент активной вкладки */}
            {activeTab === 'info' ? (
                <ApartmentForm apartmentId={apartmentId}/>
            ) : (
                <PhotoManager apartmentId={apartmentId}/>
            )}
        </div>
    );
}
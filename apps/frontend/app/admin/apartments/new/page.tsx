"use client";

import Link from 'next/link';
import ApartmentForm from '@/components/admin/apartments/ApartmentForm';

export default function NewApartmentPage() {
    return (
        <div>
            <div className="flex items-center mb-6">
                <Link href="/admin/apartments" className="text-primary-600 hover:text-primary-700 mr-2">
                    &larr; Назад к списку
                </Link>
                <h1 className="text-2xl font-bold">Добавление новой квартиры</h1>
            </div>

            <ApartmentForm/>
        </div>
    );
}
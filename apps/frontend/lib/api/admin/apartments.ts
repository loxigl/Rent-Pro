/**
 * API-клиент для работы с квартирами в админ-панели
 */

import {getAccessToken} from '@/lib/utils/admin/jwt';

// Интерфейс для создания квартиры
export interface ApartmentCreate {
    title: string;
    price_rub: number;
    rooms: number;
    floor: number;
    area_m2: number;
    address: string;
    description?: string;
    active: boolean;
}

// Интерфейс для обновления квартиры
export interface ApartmentUpdate {
    title?: string;
    price_rub?: number;
    rooms?: number;
    floor?: number;
    area_m2?: number;
    address?: string;
    description?: string;
    active?: boolean;
}

// Интерфейс для квартиры в списке
export interface ApartmentListItem {
    id: number;
    title: string;
    price_rub: number;
    rooms: number;
    area_m2: number;
    active: boolean;
    photos_count: number;
    cover_url: string | null;
    created_at: string;
}

// Интерфейс для детальной информации о квартире
export interface ApartmentDetail {
    id: number;
    title: string;
    price_rub: number;
    rooms: number;
    floor: number;
    area_m2: number;
    address: string;
    description: string | null;
    active: boolean;
    photos_count: number;
    created_at: string;
    updated_at: string;
}

// Интерфейс для ответа со списком квартир
export interface ApartmentListResponse {
    items: ApartmentListItem[];
    total: number;
    page: number;
    page_size: number;
}

// Параметры запроса списка квартир
export interface GetApartmentsParams {
    search?: string;
    page?: number;
    page_size?: number;
    sort?: 'created_at' | 'price_rub' | 'title';
    order?: 'asc' | 'desc';
    active_only?: boolean;
}

/**
 * Получение списка квартир для админ-панели
 */
export async function getAdminApartments(params: GetApartmentsParams = {}): Promise<ApartmentListResponse> {
    try {
        // Получаем токен доступа
        const token = await getAccessToken();

        // Формируем URL с параметрами
        const url = new URL('/admin/api/v1/apartments', window.location.origin);

        // Добавляем параметры запроса
        if (params.search) url.searchParams.append('search', params.search);
        if (params.page) url.searchParams.append('page', params.page.toString());
        if (params.page_size) url.searchParams.append('page_size', params.page_size.toString());
        if (params.sort) url.searchParams.append('sort', params.sort);
        if (params.order) url.searchParams.append('order', params.order);
        if (params.active_only) url.searchParams.append('active_only', params.active_only.toString());

        // Выполняем запрос
        const response = await fetch(url.toString(), {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Error fetching apartments: ${response.status}`);
        }

        return response.json();
    } catch (error) {
        console.error('Error fetching apartments:', error);
        throw error;
    }
}

/**
 * Получение детальной информации о квартире
 */
export async function getAdminApartmentById(id: number): Promise<ApartmentDetail> {
    try {
        // Получаем токен доступа
        const token = await getAccessToken();

        // Выполняем запрос
        const response = await fetch(`/admin/api/v1/apartments/${id}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Error fetching apartment details: ${response.status}`);
        }

        return response.json();
    } catch (error) {
        console.error(`Error fetching apartment ${id}:`, error);
        throw error;
    }
}

/**
 * Создание новой квартиры
 */
export async function createApartment(apartmentData: ApartmentCreate): Promise<ApartmentDetail> {
    try {
        // Получаем токен доступа
        const token = await getAccessToken();

        // Выполняем запрос
        const response = await fetch('/admin/api/v1/apartments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(apartmentData)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(
                errorData?.detail || `Error creating apartment: ${response.status}`
            );
        }

        return response.json();
    } catch (error) {
        console.error('Error creating apartment:', error);
        throw error;
    }
}

/**
 * Обновление квартиры
 */
export async function updateApartment(id: number, apartmentData: ApartmentUpdate): Promise<ApartmentDetail> {
    try {
        // Получаем токен доступа
        const token = await getAccessToken();

        // Выполняем запрос
        const response = await fetch(`/admin/api/v1/apartments/${id}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(apartmentData)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => null);
            throw new Error(
                errorData?.detail || `Error updating apartment: ${response.status}`
            );
        }

        return response.json();
    } catch (error) {
        console.error(`Error updating apartment ${id}:`, error);
        throw error;
    }
}

/**
 * Удаление квартиры
 */
export async function deleteApartment(id: number): Promise<void> {
    try {
        // Получаем токен доступа
        const token = await getAccessToken();

        // Выполняем запрос
        const response = await fetch(`/admin/api/v1/apartments/${id}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Error deleting apartment: ${response.status}`);
        }
    } catch (error) {
        console.error(`Error deleting apartment ${id}:`, error);
        throw error;
    }
}
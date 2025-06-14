/**
 * API-клиент для работы с квартирами в админ-панели
 */

import {getAccessToken} from '@/lib/utils/admin/jwt';
import {getApiUrl} from '@/lib/api/config';
import {adminRoutes} from '@/lib/api/routes';
import {log} from "node:util";

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

// Интерфейс для детальной информации о квартире
export interface ApartmentDetail {
    id: number;
    title: string;
    price_rub: number;
    rooms: number;
    floor: number;
    area_m2: number;
    address: string;
    description?: string;
    active: boolean;
    photos_count: number;
    created_at: string;
    updated_at: string;
}

// Интерфейс для элемента списка квартир
export interface ApartmentListItem {
    id: number;
    title: string;
    price_rub: number;
    rooms: number;
    area_m2: number;
    active: boolean;
    photos_count: number;
    cover_url?: string;
    created_at: string;
}

// Интерфейс для пагинированного списка квартир
export interface ApartmentListResponse {
    items: ApartmentListItem[];
    total: number;
    page: number;
    page_size: number;
}

// Интерфейс для параметров поиска квартир
export interface ApartmentSearchParams {
    search?: string;
    page?: number;
    page_size?: number;
    sort?: string;
    order?: string;
    active_only?: boolean;
}

/**
 * Получение списка квартир для админ-панели с возможностью поиска
 */
export async function getApartments(params: ApartmentSearchParams = {}): Promise<ApartmentListResponse> {
    try {
        const token = getAccessToken();

        if (!token) {
            throw new Error('Необходима авторизация');
        }

        // Формируем URL с параметрами
        const url = new URL(`${getApiUrl(adminRoutes.apartments.list)}`);


        // Добавляем параметры запроса
        if (params.search) url.searchParams.append('search', params.search);
        if (params.page) url.searchParams.append('page', params.page.toString());
        if (params.page_size) url.searchParams.append('page_size', params.page_size.toString());
        if (params.sort) url.searchParams.append('sort', params.sort);
        if (params.order) url.searchParams.append('order', params.order);
        if (params.active_only !== undefined) url.searchParams.append('active_only', params.active_only.toString());

        const response = await fetch(url.toString(), {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Ошибка получения списка квартир: ${response.status} ${errorText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Ошибка при получении списка квартир:', error);
        // В случае ошибки возвращаем пустой список
        return {
            items: [],
            total: 0,
            page: 1,
            page_size: 10
        };
    }
}

/**
 * Получение информации о квартире по ID
 */
export async function getApartmentById(id: number): Promise<ApartmentDetail> {
    try {
        const token = getAccessToken();

        if (!token) {
            throw new Error('Необходима авторизация');
        }

        const response = await fetch(getApiUrl(adminRoutes.apartments.detail(id)), {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Ошибка получения информации о квартире: ${response.status} ${errorText}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`Ошибка при получении информации о квартире (ID: ${id}):`, error);
        throw error;
    }
}

/**
 * Создание новой квартиры
 */
export async function createApartment(data: ApartmentCreate): Promise<ApartmentDetail> {
    try {
        const token = getAccessToken();

        if (!token) {
            throw new Error('Необходима авторизация');
        }

        const response = await fetch(getApiUrl(adminRoutes.apartments.create), {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Ошибка создания квартиры: ${response.status} ${errorText}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Ошибка при создании квартиры:', error);
        throw error;
    }
}

/**
 * Обновление информации о квартире
 */
export async function updateApartment(id: number, data: ApartmentUpdate): Promise<ApartmentDetail> {
    try {
        const token = getAccessToken();

        if (!token) {
            throw new Error('Необходима авторизация');
        }

        const response = await fetch(getApiUrl(adminRoutes.apartments.update(id)), {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Ошибка обновления квартиры: ${response.status} ${errorText}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`Ошибка при обновлении квартиры (ID: ${id}):`, error);
        throw error;
    }
}

/**
 * Удаление квартиры
 */
export async function deleteApartment(id: number): Promise<void> {
    try {
        const token = getAccessToken();

        if (!token) {
            throw new Error('Необходима авторизация');
        }

        const response = await fetch(getApiUrl(adminRoutes.apartments.delete(id)), {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Ошибка удаления квартиры: ${response.status} ${errorText}`);
        }
    } catch (error) {
        console.error(`Ошибка при удалении квартиры (ID: ${id}):`, error);
        throw error;
    }
}

/**
 * Включение/отключение возможности бронирования для квартиры
 */
export async function toggleBooking(id: number, enable: boolean): Promise<any> {
    try {
        const token = getAccessToken();

        if (!token) {
            throw new Error('Необходима авторизация');
        }

        const url = new URL(getApiUrl(adminRoutes.apartments.bookingToggle(id)));
        url.searchParams.append('enable', enable.toString());

        const response = await fetch(url.toString(), {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Ошибка изменения статуса бронирования: ${response.status} ${errorText}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`Ошибка при изменении статуса бронирования квартиры (ID: ${id}):`, error);
        throw error;
    }
}
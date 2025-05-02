/**
 * Типы данных для работы с API квартир
 */

// Квартира в списке
export interface ApartmentListItem {
    id: number;
    title: string;
    price_rub: number;
    rooms: number;
    floor: number;
    area_m2: number;
    cover_url: string | null;
}

// Ответ с пагинацией
export interface ApartmentListResponse {
    page: number;
    page_size: number;
    total: number;
    items: ApartmentListItem[];
}

// Детальная информация о квартире
export interface ApartmentDetail {
    id: number;
    title: string;
    price_rub: number;
    rooms: number;
    floor: number;
    area_m2: number;
    address: string;
    description: string;
    active: boolean;
    booking_enabled: boolean;
    photos: string[];
    created_at: string;
}

// Параметры запроса списка квартир
export interface GetApartmentsParams {
    page?: number;
    page_size?: number;
    sort?: 'created_at' | 'price_rub';
    order?: 'asc' | 'desc';
}

// Исправляем потенциальное дублирование /api
import { getApiUrl } from './config';

/**
 * Получение списка квартир с пагинацией и сортировкой
 */
export async function getApartments(params: GetApartmentsParams = {}): Promise<ApartmentListResponse> {
    // В статическом режиме возвращаем пустые данные
    if (process.env.BUILD_MODE === 'static') {
        return {
            page: 1,
            page_size: 12,
            total: 0,
            items: []
        };
    }

    const {
        page = 1,
        page_size = 12,
        sort = 'created_at',
        order = 'desc'
    } = params;

    const searchParams = new URLSearchParams({
        page: page.toString(),
        page_size: page_size.toString(),
        sort,
        order,
    });

    try {
        const response = await fetch(getApiUrl(`/apartments?${searchParams.toString()}`));

        if (!response.ok) {
            throw new Error(`Failed to fetch apartments: ${response.status}, url: ${response.url}`);
        }

        return response.json();
    } catch (error) {
        console.error("Error fetching apartments:", error);
        // Возвращаем пустые данные при ошибке
        return {
            page: 1,
            page_size: 12,
            total: 0,
            items: []
        };
    }
}

/**
 * Получение детальной информации о квартире по ID
 */
export async function getApartmentById(id: number): Promise<ApartmentDetail> {
    // В статическом режиме возвращаем мок-данные
    if (process.env.BUILD_MODE === 'static') {
        return {
            id,
            title: "Временные данные для сборки",
            price_rub: 2000,
            rooms: 2,
            floor: 3,
            area_m2: 50,
            address: "г. Невинномысск",
            description: "Временное описание для статической сборки",
            active: true,
            booking_enabled: true,
            photos: [],
            created_at: new Date().toISOString()
        };
    }

    try {
        const response = await fetch(getApiUrl(`/apartments/${id}`));

        if (!response.ok) {
            throw new Error(`Failed to fetch apartment with id ${id}: ${response.status}, url: ${response.url}`);
        }

        return response.json();
    } catch (error) {
        console.error(`Error fetching apartment ${id}:`, error);
        // Возвращаем мок-данные при ошибке
        return {
            id,
            title: "Данные недоступны",
            price_rub: 0,
            rooms: 0,
            floor: 0,
            area_m2: 0,
            address: "Адрес недоступен",
            description: "Не удалось загрузить данные",
            active: false,
            booking_enabled: false,
            photos: [],
            created_at: new Date().toISOString()
        };
    }
}

/**
 * Загрузка фотографии для квартиры (только для админа)
 */
export async function uploadApartmentPhoto(
    apartmentId: number,
    file: File
): Promise<{ id: number; url: string; apartment_id: number; sort_order: number }> {
    const formData = new FormData();
    formData.append('apartment_id', apartmentId.toString());
    formData.append('file', file);

    const response = await fetch(getApiUrl('/admin/upload'), {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error(`Failed to upload photo: ${response.status}, url: ${response.url}`);
    }

    return response.json();
}
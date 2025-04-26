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

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Получение списка квартир с пагинацией и сортировкой
 */
export async function getApartments(params: GetApartmentsParams = {}): Promise<ApartmentListResponse> {
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

    const response = await fetch(`${API_URL}/api/v1/apartments?${searchParams.toString()}`);

    if (!response.ok) {
        throw new Error(`Failed to fetch apartments: ${response.status}`);
    }

    return response.json();
}

/**
 * Получение детальной информации о квартире по ID
 */
export async function getApartmentById(id: number): Promise<ApartmentDetail> {
    const response = await fetch(`${API_URL}/api/v1/apartments/${id}`);

    if (!response.ok) {
        throw new Error(`Failed to fetch apartment with id ${id}: ${response.status}`);
    }

    return response.json();
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

    const response = await fetch(`${API_URL}/api/v1/admin/upload`, {
        method: 'POST',
        body: formData,
    });

    if (!response.ok) {
        throw new Error(`Failed to upload photo: ${response.status}`);
    }

    return response.json();
}
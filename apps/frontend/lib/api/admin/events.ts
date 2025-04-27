/**
 * API-клиент для работы с журналом событий в админ-панели
 */

import {getAccessToken} from '@/lib/utils/admin/jwt';

// Типы событий
export type EventType =
    | 'user_login'
    | 'user_logout'
    | 'apartment_created'
    | 'apartment_updated'
    | 'apartment_deleted'
    | 'photo_uploaded'
    | 'photo_deleted'
    | 'photo_updated';

// Типы сущностей
export type EntityType = 'apartment' | 'photo' | 'user';

// Интерфейс события
export interface EventLogItem {
    id: string;
    timestamp: string;
    user_id?: number;
    user_email?: string;
    event_type: string;
    entity_type?: string;
    entity_id?: string;
    ip_address?: string;
    user_agent?: string;
    payload?: any;
}

// Интерфейс ответа со списком событий
export interface EventLogResponse {
    items: EventLogItem[];
    total: number;
    page: number;
    page_size: number;
}

// Параметры запроса списка событий
export interface GetEventsParams {
    page?: number;
    page_size?: number;
    user_id?: number;
    event_type?: EventType;
    entity_type?: EntityType;
    start_date?: string;
    end_date?: string;
}

// Получение списка событий с фильтрацией и пагинацией
export async function getEvents(params: GetEventsParams = {}): Promise<EventLogResponse> {
    try {
        // Получаем токен доступа
        const token = await getAccessToken();

        // Формируем URL с параметрами
        const url = new URL('/admin/api/v1/events', window.location.origin);

        // Добавляем параметры запроса
        if (params.page) url.searchParams.append('page', params.page.toString());
        if (params.page_size) url.searchParams.append('page_size', params.page_size.toString());
        if (params.user_id) url.searchParams.append('user_id', params.user_id.toString());
        if (params.event_type) url.searchParams.append('event_type', params.event_type);
        if (params.entity_type) url.searchParams.append('entity_type', params.entity_type);
        if (params.start_date) url.searchParams.append('start_date', params.start_date);
        if (params.end_date) url.searchParams.append('end_date', params.end_date);

        // Выполняем запрос
        const response = await fetch(url.toString(), {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Error fetching events: ${response.status}`);
        }

        return response.json();
    } catch (error) {
        console.error('Error fetching events:', error);
        throw error;
    }
}

// Получение детальной информации о событии
export async function getEventById(eventId: string): Promise<EventLogItem> {
    try {
        // Получаем токен доступа
        const token = await getAccessToken();

        // Выполняем запрос
        const response = await fetch(`/admin/api/v1/events/${eventId}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Error fetching event details: ${response.status}`);
        }

        return response.json();
    } catch (error) {
        console.error(`Error fetching event ${eventId}:`, error);
        throw error;
    }
}

// Получение статистики по типам событий
export async function getEventStats(
    startDate?: string,
    endDate?: string
): Promise<Record<string, number>> {
    try {
        // Получаем токен доступа
        const token = await getAccessToken();

        // Формируем URL с параметрами
        const url = new URL('/admin/api/v1/events/stats/summary', window.location.origin);

        // Добавляем параметры запроса
        if (startDate) url.searchParams.append('start_date', startDate);
        if (endDate) url.searchParams.append('end_date', endDate);

        // Выполняем запрос
        const response = await fetch(url.toString(), {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error(`Error fetching event stats: ${response.status}`);
        }

        return response.json();
    } catch (error) {
        console.error('Error fetching event stats:', error);
        throw error;
    }
}
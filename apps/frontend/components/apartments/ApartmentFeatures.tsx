import {formatArea, formatFloor, formatRooms} from "@/lib/utils/format";

interface ApartmentFeaturesProps {
    rooms: number;
    area_m2: number;
    floor: number;
    address: string;
}

/**
 * Компонент для отображения характеристик квартиры в таблице
 */
export default function ApartmentFeatures({
                                              rooms,
                                              area_m2,
                                              floor,
                                              address
                                          }: ApartmentFeaturesProps) {
    // Список всех характеристик для отображения
    const features = [
        {name: "Комнат", value: formatRooms(rooms)},
        {name: "Площадь", value: formatArea(area_m2)},
        {name: "Этаж", value: formatFloor(floor)},
        {name: "Адрес", value: address},
    ];

    return (
        <div className="bg-secondary-50 rounded-lg p-5 my-6">
            <h3 className="text-lg font-semibold mb-4">Характеристики</h3>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {features.map((feature) => (
                    <div key={feature.name} className="flex justify-between">
                        <span className="text-secondary-600">{feature.name}:</span>
                        <span className="font-medium">{feature.value}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

/**
 * Компонент скелетона для характеристик квартиры
 */
export function ApartmentFeaturesSkeleton() {
    return (
        <div className="bg-secondary-50 rounded-lg p-5 my-6">
            <div className="h-6 w-40 bg-secondary-200 animate-skeleton-pulse rounded mb-4"/>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {Array.from({length: 4}).map((_, index) => (
                    <div key={index} className="flex justify-between">
                        <div className="h-5 w-24 bg-secondary-200 animate-skeleton-pulse rounded"/>
                        <div className="h-5 w-32 bg-secondary-200 animate-skeleton-pulse rounded"/>
                    </div>
                ))}
            </div>
        </div>
    );
}
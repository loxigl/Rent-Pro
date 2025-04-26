import {HTMLAttributes} from "react";
import {cn} from "@/lib/utils/cn";

interface SkeletonProps extends HTMLAttributes<HTMLDivElement> {
}

/**
 * Компонент Skeleton для отображения состояния загрузки контента
 */
export function Skeleton({className, ...props}: SkeletonProps) {
    return (
        <div
            className={cn("skeleton", className)}
            {...props}
        />
    );
}

/**
 * Компонент SkeletonCard для отображения плейсхолдера карточки квартиры
 */
export function SkeletonCard() {
    return (
        <div className="card">
            <Skeleton className="w-full h-48"/>
            <div className="p-4 space-y-3">
                <Skeleton className="h-6 w-3/4"/>
                <Skeleton className="h-4 w-1/2"/>
                <Skeleton className="h-5 w-1/3"/>
            </div>
        </div>
    );
}

/**
 * Компонент SkeletonGrid для отображения сетки плейсхолдеров
 */
export function SkeletonGrid({count = 6}: { count?: number }) {
    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {Array.from({length: count}).map((_, index) => (
                <SkeletonCard key={index}/>
            ))}
        </div>
    );
}
import {ButtonHTMLAttributes, forwardRef} from "react";
import {cn} from "@/lib/utils/cn";

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: "primary" | "secondary" | "outline" | "link";
    size?: "sm" | "md" | "lg";
    fullWidth?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
    ({
         children,
         className,
         variant = "primary",
         size = "md",
         fullWidth,
         ...props
     }, ref) => {
        return (
            <button
                className={cn(
                    // Базовые стили для всех кнопок
                    "inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",

                    // Варианты стилей
                    {
                        "bg-primary-600 text-white hover:bg-primary-700": variant === "primary",
                        "bg-white text-secondary-700 hover:bg-secondary-50 ring-1 ring-inset ring-secondary-300":
                            variant === "secondary",
                        "bg-transparent text-secondary-900 hover:bg-secondary-100 ring-1 ring-inset ring-secondary-300":
                            variant === "outline",
                        "bg-transparent text-primary-600 hover:text-primary-700 hover:underline p-0":
                            variant === "link",
                    },

                    // Размеры
                    {
                        "text-sm px-3 py-2": size === "sm",
                        "text-sm px-4 py-2": size === "md",
                        "text-base px-5 py-3": size === "lg",
                    },

                    // Полная ширина
                    fullWidth && "w-full",

                    className
                )}
                ref={ref}
                {...props}
            >
                {children}
            </button>
        );
    }
);

Button.displayName = "Button";

export {Button};
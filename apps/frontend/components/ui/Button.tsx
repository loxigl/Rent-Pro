import React, {ElementType, forwardRef} from "react";
import {cn} from "@/lib/utils/cn";

type ButtonVariant = "primary" | "secondary" | "outline" | "link";
type ButtonSize = "sm" | "md" | "lg";

interface BaseButtonProps {
    variant?: ButtonVariant;
    size?: ButtonSize;
    fullWidth?: boolean;
    className?: string;
    children?: React.ReactNode;
}

type ButtonProps<C extends ElementType = "button"> = {
    as?: C;
} & BaseButtonProps & Omit<React.ComponentPropsWithoutRef<C>, keyof BaseButtonProps | "as">;

const Button = forwardRef(
    <C extends ElementType = "button">(
        {
            as,
            children,
            className,
            variant = "primary",
            size = "md",
            fullWidth,
            ...props
        }: ButtonProps<C>,
        ref: React.Ref<any> // чуть проще реф
    ) => {
        const Component = as || "button";

        return (
            <Component
                ref={ref}
                className={cn(
                    "inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",
                    {
                        "bg-primary-600 text-white hover:bg-primary-700": variant === "primary",
                        "bg-white text-secondary-700 hover:bg-secondary-50 ring-1 ring-inset ring-secondary-300": variant === "secondary",
                        "bg-transparent text-secondary-900 hover:bg-secondary-100 ring-1 ring-inset ring-secondary-300": variant === "outline",
                        "bg-transparent text-primary-600 hover:text-primary-700 hover:underline p-0": variant === "link",
                    },
                    {
                        "text-sm px-3 py-2": size === "sm",
                        "text-sm px-4 py-2": size === "md",
                        "text-base px-5 py-3": size === "lg",
                    },
                    fullWidth && "w-full",
                    className
                )}
                {...props}
            >
                {children}
            </Component>
        );
    }
);

Button.displayName = "Button";

export {Button};
export type {ButtonProps};

"use client";

import ReactMarkdown from "react-markdown";
import {cn} from "@/lib/utils/cn";

interface MarkdownProps {
    content: string;
    className?: string;
}

/**
 * Компонент для отображения Markdown контента
 */
export function Markdown({content, className}: MarkdownProps) {
    return (
        <ReactMarkdown
            className = {
            cn(
            "prose prose-sm md:prose-base max-w-none",
            "prose-headings:font-semibold prose-headings:text-secondary-900",
            "prose-p:text-secondary-700",
            "prose-strong:text-secondary-900",
            "prose-ul:text-secondary-700",
            "prose-li:marker:text-primary-500",
            className
    )
}
    components = {
    {
        // Кастомизация компонентов Markdown
        h1: ({node, ...props}) => (
            <h1 className = "text-2xl font-bold mb-4 mt-6"
        {...
            props
        }
        />
    ),
        h2: ({node, ...props}) => (
            <h2 className = "text-xl font-bold mb-3 mt-5"
        {...
            props
        }
        />
    ),
        h3: ({node, ...props}) => (
            <h3 className = "text-lg font-bold mb-3 mt-4"
        {...
            props
        }
        />
    ),
        a: ({node, ...props}) => (
            <a
                className = "text-primary-600 hover:text-primary-800 hover:underline"
        target = "_blank"
        rel = "noopener noreferrer"
        {...
            props
        }
        />
    ),
        ul: ({node, ...props}) => (
            <ul className = "list-disc pl-5 my-3"
        {...
            props
        }
        />
    ),
        ol: ({node, ...props}) => (
            <ol className = "list-decimal pl-5 my-3"
        {...
            props
        }
        />
    ),
        // Прочие компоненты останутся со стандартными стилями Tailwind Prose
    }
}
>
    {
        content
    }
    </ReactMarkdown>
)
    ;
}
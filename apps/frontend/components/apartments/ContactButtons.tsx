import { Button } from "@/components/ui/Button";
import { formatPhoneUrl, formatTelegramUrl } from "@/lib/utils/format";

interface ContactButtonsProps {
  phone?: string;
  telegram?: string;
}

/**
 * Компонент кнопок для связи с арендодателем
 */
export default function ContactButtons({
  phone = "+79991234567",  // По умолчанию используем тестовый телефон
  telegram = "avitorentpro" // По умолчанию используем тестовый аккаунт Telegram
}: ContactButtonsProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-4 my-6">
      <Button
        as="a"
        href={formatPhoneUrl(phone)}
        variant="primary"
        size="lg"
        className="flex-1 justify-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
        </svg>
        Позвонить
      </Button>

      <Button
        as="a"
        href={formatTelegramUrl(telegram)}
        variant="secondary"
        size="lg"
        target="_blank"
        rel="noopener noreferrer"
        className="flex-1 justify-center gap-2"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21.5 2h-19C1.67 2 1 2.67 1 3.5v17c0 .83.67 1.5 1.5 1.5h19c.83 0 1.5-.67 1.5-1.5v-17c0-.83-.67-1.5-1.5-1.5zM5 8.5A1.5 1.5 0 1 1 6.5 10 1.5 1.5 0 0 1 5 8.5zM12 18c-3 0-5.5-2.5-5.5-5.5S9 7 12 7s5.5 2.5 5.5 5.5-2.5 5.5-5.5 5.5zm9-7a1.5 1.5 0 1 1-1.5-1.5 1.5 1.5 0 0 1 1.5 1.5z" />
        </svg>
        Написать в TG
      </Button>
    </div>
  );
}
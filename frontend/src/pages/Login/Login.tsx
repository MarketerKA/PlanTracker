import { FC, useState, FormEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Login.module.scss';
import { 
  AuthLayout, 
  InputField, 
  Button, 
  EmailIcon, 
  LockIcon,
  EyeIcon,
  EyeOffIcon
} from '../../components';
import { ROUTES } from '../../routes';

export interface LoginProps {}

export const Login: FC<LoginProps> = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<{email?: string; password?: string}>({});
  const [isLoading, setIsLoading] = useState(false);

  const togglePasswordVisibility = () => {
    setShowPassword(prev => !prev);
  };

  const validateForm = () => {
    const newErrors: {email?: string; password?: string} = {};
    
    if (!email) {
      newErrors.email = 'Email обязателен';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Некорректный email';
    }
    
    if (!password) {
      newErrors.password = 'Пароль обязателен';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsLoading(true);
    
    try {
      // Здесь будет запрос на авторизацию
      console.log('Попытка входа с:', { email, password });
      
      // Имитация API-запроса
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // В реальном приложении здесь будет обработка ответа от API
      // и сохранение токена/пользователя
      console.log('Успешный вход');
      
      // Перенаправление на главную страницу
      navigate(ROUTES.HOME);
    } catch (error) {
      console.error('Ошибка при авторизации:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const goToRegister = () => {
    navigate(ROUTES.REGISTER);
  };

  return (
    <AuthLayout 
      title="Вход в аккаунт" 
      subtitle="Введите ваши данные для доступа к сервису"
    >
      <form className={styles.form} onSubmit={handleSubmit}>
        <InputField
          label="Email"
          icon={<EmailIcon />}
          type="email"
          placeholder="your@email.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          error={errors.email}
        />
        
        <InputField
          label="Пароль"
          icon={<LockIcon />}
          type={showPassword ? 'text' : 'password'}
          placeholder="Введите пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          error={errors.password}
          rightIcon={showPassword ? <EyeOffIcon /> : <EyeIcon />}
          onRightIconClick={togglePasswordVisibility}
        />
        
        <div className={styles.forgotPassword}>
          <a href="#" className={styles.link}>Забыли пароль?</a>
        </div>
        
        <Button
          type="submit"
          disabled={isLoading}
          className={styles.submitButton}
        >
          {isLoading ? 'Вход...' : 'Войти'}
        </Button>
        
        <div className={styles.registerPrompt}>
          <span>Еще нет аккаунта?</span>
          <button 
            type="button" 
            className={styles.registerLink}
            onClick={goToRegister}
          >
            Зарегистрироваться
          </button>
        </div>
      </form>
    </AuthLayout>
  );
}; 
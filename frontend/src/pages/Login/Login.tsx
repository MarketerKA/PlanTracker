import { FC, useState, FormEvent, useEffect } from 'react';
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
import { useAppDispatch, useAppSelector } from '../../redux/hooks';
import { login, clearError } from '../../redux/auth';

export interface LoginProps {}

export const Login: FC<LoginProps> = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { loading, error, isAuthenticated } = useAppSelector(state => state.auth);
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [formErrors, setFormErrors] = useState<{email?: string; password?: string}>({});

  // Если пользователь уже авторизован, перенаправляем на главную страницу
  useEffect(() => {
    if (isAuthenticated) {
      navigate(ROUTES.HOME);
    }
  }, [isAuthenticated, navigate]);

  // Сбрасываем ошибки с сервера при изменении полей ввода
  useEffect(() => {
    if (error) {
      dispatch(clearError());
    }
  }, [email, password, dispatch, error]);

  const togglePasswordVisibility = () => {
    setShowPassword(prev => !prev);
  };

  const validateForm = (): boolean => {
    const newErrors: {email?: string; password?: string} = {};
    
    if (!email) {
      newErrors.email = 'Email обязателен';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Некорректный email';
    }
    
    if (!password) {
      newErrors.password = 'Пароль обязателен';
    }
    
    setFormErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    // Отправляем запрос на авторизацию через Redux
    dispatch(login({ email, password }));
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
        {error && (
          <div className={styles.serverError}>
            {error}
          </div>
        )}
        
        <InputField
          label="Email"
          icon={<EmailIcon />}
          type="email"
          placeholder="your@email.com"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          error={formErrors.email}
        />
        
        <InputField
          label="Пароль"
          icon={<LockIcon />}
          type={showPassword ? 'text' : 'password'}
          placeholder="Введите пароль"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          error={formErrors.password}
          rightIcon={showPassword ? <EyeOffIcon /> : <EyeIcon />}
          onRightIconClick={togglePasswordVisibility}
        />
        
        <div className={styles.forgotPassword}>
          <a href="#" className={styles.link}>Забыли пароль?</a>
        </div>
        
        <Button
          type="submit"
          disabled={loading}
          className={styles.submitButton}
        >
          {loading ? 'Вход...' : 'Войти'}
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
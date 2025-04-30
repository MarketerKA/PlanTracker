import { FC, useState, FormEvent, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './Register.module.scss';
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
import { register, clearError } from '../../redux/auth';

export interface RegisterProps {}

export const Register: FC<RegisterProps> = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { loading, error, isAuthenticated } = useAppSelector(state => state.auth);
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formErrors, setFormErrors] = useState<{
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});

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
  }, [email, password, confirmPassword, dispatch, error]);

  const togglePasswordVisibility = () => {
    setShowPassword(prev => !prev);
  };

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(prev => !prev);
  };

  const validateForm = (): boolean => {
    const newErrors: {
      email?: string;
      password?: string;
      confirmPassword?: string;
    } = {};
    
    if (!email) {
      newErrors.email = 'Email обязателен';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Некорректный email';
    }
    
    if (!password) {
      newErrors.password = 'Пароль обязателен';
    } else if (password.length < 8) {
      newErrors.password = 'Пароль должен содержать минимум 8 символов';
    }
    
    if (password !== confirmPassword) {
      newErrors.confirmPassword = 'Пароли не совпадают';
    }
    
    setFormErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    // Отправляем запрос на регистрацию через Redux
    dispatch(register({ email, password }));
  };

  const goToLogin = () => {
    navigate(ROUTES.LOGIN);
  };

  return (
    <AuthLayout 
      title="Регистрация" 
      subtitle="Создайте аккаунт для доступа к сервису"
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
          placeholder="Минимум 8 символов"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          error={formErrors.password}
          rightIcon={showPassword ? <EyeOffIcon /> : <EyeIcon />}
          onRightIconClick={togglePasswordVisibility}
        />
        
        <InputField
          label="Подтверждение пароля"
          icon={<LockIcon />}
          type={showConfirmPassword ? 'text' : 'password'}
          placeholder="Повторите пароль"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          required
          error={formErrors.confirmPassword}
          rightIcon={showConfirmPassword ? <EyeOffIcon /> : <EyeIcon />}
          onRightIconClick={toggleConfirmPasswordVisibility}
        />
        
        <Button
          type="submit"
          disabled={loading}
          className={styles.submitButton}
        >
          {loading ? 'Регистрация...' : 'Зарегистрироваться'}
        </Button>
        
        <div className={styles.loginPrompt}>
          <span>Уже есть аккаунт?</span>
          <button 
            type="button" 
            className={styles.loginLink}
            onClick={goToLogin}
          >
            Войти
          </button>
        </div>
      </form>
    </AuthLayout>
  );
}; 
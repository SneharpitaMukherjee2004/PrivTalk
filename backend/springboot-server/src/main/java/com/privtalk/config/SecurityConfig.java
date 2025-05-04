package com.privtalk.config;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.client.RestTemplate;

                
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .authorizeHttpRequests(auth -> auth
                                .requestMatchers("/auth/**").permitAll()
                                .anyRequest().authenticated()
                )
                .formLogin(form -> form
                                .loginPage("/login.html") // your custom login, or remove for default
                                .permitAll()
                )
                .logout(logout -> logout
                                .logoutUrl("/auth/logout")
                                .logoutSuccessUrl("/login?logout") // or wherever you want
                                .deleteCookies("JSESSIONID")       // deletes session cookie
                                .invalidateHttpSession(true)       // clears session
                                .permitAll()
                );

       
        return http.build();
    }
}

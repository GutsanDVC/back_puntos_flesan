"""Script de prueba para verificar el CRUD de beneficios"""

import asyncio
import json
from datetime import datetime
from uuid import uuid4

from app.domain.beneficios.entities.beneficio import Beneficio
from app.domain.beneficios.services.beneficio_service import BeneficioService
from app.application.beneficios.dto import CreateBeneficioDTO, UpdateBeneficioDTO, BeneficioFilterDTO


def test_beneficio_entity():
    """Prueba la entidad de dominio Beneficio"""
    print("🧪 Probando entidad Beneficio...")
    
    # Crear beneficio válido
    beneficio = Beneficio(
        id=uuid4(),
        imagen="test/image.png",
        beneficio="Test Beneficio",
        detalle="Detalle de prueba",
        regla1="Regla 1",
        regla2="Regla 2",
        valor=100,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    assert beneficio.beneficio == "Test Beneficio"
    assert beneficio.valor == 100
    assert beneficio.is_active == True
    
    # Probar métodos de dominio
    beneficio.deactivate()
    assert beneficio.is_active == False
    
    beneficio.activate()
    assert beneficio.is_active == True
    
    beneficio.update_value(200)
    assert beneficio.valor == 200
    
    print("✅ Entidad Beneficio funciona correctamente")


def test_beneficio_service():
    """Prueba los servicios de dominio"""
    print("🧪 Probando servicios de dominio...")
    
    beneficios = [
        Beneficio(
            id=uuid4(),
            imagen="test1.png",
            beneficio="Beneficio 1",
            detalle="Detalle 1",
            regla1="Regla 1",
            regla2="Regla 2",
            valor=100,
            is_active=True,
            created_at=datetime.utcnow()
        ),
        Beneficio(
            id=uuid4(),
            imagen="test2.png",
            beneficio="Beneficio 2",
            detalle="Detalle 2",
            regla1="Regla 1",
            regla2="Regla 2",
            valor=200,
            is_active=False,
            created_at=datetime.utcnow()
        )
    ]
    
    # Probar validación de unicidad
    is_unique = BeneficioService.validate_beneficio_name_uniqueness(
        beneficios, "Beneficio Nuevo"
    )
    assert is_unique == True
    
    is_unique = BeneficioService.validate_beneficio_name_uniqueness(
        beneficios, "Beneficio 1"
    )
    assert is_unique == False
    
    # Probar cálculo de valor total
    valor_total = BeneficioService.calculate_total_value(beneficios)
    assert valor_total == 100  # Solo el activo
    
    # Probar filtro de activos
    activos = BeneficioService.filter_active_beneficios(beneficios)
    assert len(activos) == 1
    assert activos[0].beneficio == "Beneficio 1"
    
    # Probar ordenamiento por valor
    ordenados = BeneficioService.sort_by_value(beneficios, descending=True)
    assert ordenados[0].valor == 200
    assert ordenados[1].valor == 100
    
    print("✅ Servicios de dominio funcionan correctamente")


def test_dtos():
    """Prueba los DTOs"""
    print("🧪 Probando DTOs...")
    
    # CreateBeneficioDTO
    create_dto = CreateBeneficioDTO(
        imagen="test.png",
        beneficio="Test DTO",
        detalle="Detalle DTO",
        regla1="Regla 1",
        regla2="Regla 2",
        valor=150
    )
    
    assert create_dto.beneficio == "Test DTO"
    assert create_dto.valor == 150
    
    # UpdateBeneficioDTO
    update_dto = UpdateBeneficioDTO(
        beneficio="Test DTO Actualizado",
        valor=200
    )
    
    assert update_dto.beneficio == "Test DTO Actualizado"
    assert update_dto.valor == 200
    assert update_dto.imagen is None  # Campo opcional
    
    # BeneficioFilterDTO
    filter_dto = BeneficioFilterDTO(
        page=2,
        size=20,
        is_active=True
    )
    
    assert filter_dto.page == 2
    assert filter_dto.size == 20
    assert filter_dto.is_active == True
    
    print("✅ DTOs funcionan correctamente")


def test_validations():
    """Prueba las validaciones de dominio"""
    print("🧪 Probando validaciones...")
    
    # Beneficio con nombre vacío debe fallar
    try:
        beneficio = Beneficio(
            id=uuid4(),
            imagen="test.png",
            beneficio="",  # Vacío
            detalle="Detalle",
            regla1="Regla 1",
            regla2="Regla 2",
            valor=100,
            is_active=True,
            created_at=datetime.utcnow()
        )
        assert False, "Debería haber fallado con nombre vacío"
    except ValueError as e:
        assert "beneficio es requerido" in str(e)
    
    # Valor negativo debe fallar
    try:
        beneficio = Beneficio(
            id=uuid4(),
            imagen="test.png",
            beneficio="Test",
            detalle="Detalle",
            regla1="Regla 1",
            regla2="Regla 2",
            valor=-100,  # Negativo
            is_active=True,
            created_at=datetime.utcnow()
        )
        assert False, "Debería haber fallado con valor negativo"
    except ValueError as e:
        assert "no puede ser negativo" in str(e)
    
    print("✅ Validaciones funcionan correctamente")


def main():
    """Ejecuta todas las pruebas"""
    print("🚀 Iniciando pruebas del CRUD de Beneficios...\n")
    
    try:
        test_beneficio_entity()
        print()
        
        test_beneficio_service()
        print()
        
        test_dtos()
        print()
        
        test_validations()
        print()
        
        print("🎉 ¡Todas las pruebas pasaron exitosamente!")
        print("\n📋 Resumen:")
        print("✅ Entidad de dominio Beneficio")
        print("✅ Servicios de dominio")
        print("✅ DTOs de aplicación")
        print("✅ Validaciones de negocio")
        print("\n🚀 El CRUD de beneficios está listo para usar!")
        
    except Exception as e:
        print(f"❌ Error en las pruebas: {e}")
        raise


if __name__ == "__main__":
    main()

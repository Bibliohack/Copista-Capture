#!/bin/bash

# =================================================================
# Script para obtener la configuración completa de una cámara gphoto2
# Uso: ./gphoto_config_dump.sh [archivo_salida]
# =================================================================

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuración
OUTPUT_FILE="${1:-camera_config_$(date +%Y%m%d_%H%M%S).txt}"
TEMP_LIST="/tmp/gphoto_config_list.tmp"
ERROR_LOG="/tmp/gphoto_errors.log"

# Función para mostrar ayuda
show_help() {
    echo -e "${BLUE}==================================================================="
    echo -e "  Script para obtener configuración completa de cámara gphoto2"
    echo -e "===================================================================${NC}"
    echo
    echo -e "${CYAN}USO:${NC}"
    echo -e "  $0 [archivo_salida]"
    echo
    echo -e "${CYAN}EJEMPLOS:${NC}"
    echo -e "  $0                           # Salida: camera_config_TIMESTAMP.txt"
    echo -e "  $0 mi_camara.txt            # Salida: mi_camara.txt"
    echo -e "  $0 /tmp/config.txt          # Salida en /tmp/config.txt"
    echo
    echo -e "${CYAN}OPCIONES:${NC}"
    echo -e "  -h, --help                   Mostrar esta ayuda"
    echo -e "  -v, --verbose               Modo verbose (mostrar progreso)"
    echo -e "  -j, --json                  Formato de salida JSON"
    echo -e "  -c, --check                 Solo verificar conexión con cámara"
    echo
}

# Variables de configuración
VERBOSE=false
JSON_OUTPUT=false
CHECK_ONLY=false

# Procesar argumentos
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -j|--json)
            JSON_OUTPUT=true
            shift
            ;;
        -c|--check)
            CHECK_ONLY=true
            shift
            ;;
        -*)
            echo -e "${RED}Error: Opción desconocida $1${NC}" >&2
            show_help
            exit 1
            ;;
        *)
            OUTPUT_FILE="$1"
            shift
            ;;
    esac
done

# Función para logging verbose
log_verbose() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${CYAN}[INFO]${NC} $1" >&2
    fi
}

# Función para mostrar errores
log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Función para mostrar avisos
log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" >&2
}

# Función para mostrar éxito
log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" >&2
}

# Verificar que gphoto2 esté instalado
check_gphoto2() {
    if ! command -v gphoto2 &> /dev/null; then
        log_error "gphoto2 no está instalado. Instálalo con:"
        echo "  Ubuntu/Debian: sudo apt-get install gphoto2"
        echo "  Fedora/CentOS: sudo dnf install gphoto2"
        echo "  Arch Linux: sudo pacman -S gphoto2"
        exit 1
    fi
    log_verbose "gphoto2 encontrado: $(which gphoto2)"
}

# Verificar conexión con cámara
check_camera_connection() {
    log_verbose "Verificando conexión con cámara..."
    
    if ! gphoto2 --auto-detect > /dev/null 2>&1; then
        log_error "No se pudo detectar ninguna cámara"
        echo
        echo "Soluciones posibles:"
        echo "1. Asegúrate de que la cámara esté encendida y conectada"
        echo "2. Verifica que esté en modo PTP (no Mass Storage)"
        echo "3. Ejecuta: gphoto2 --auto-detect"
        exit 1
    fi
    
    # Mostrar cámaras detectadas
    CAMERA_INFO=$(gphoto2 --auto-detect 2>/dev/null | tail -n +3)
    if [ -n "$CAMERA_INFO" ]; then
        log_success "Cámaras detectadas:"
        echo "$CAMERA_INFO" | while read -r line; do
            if [ -n "$line" ]; then
                echo -e "${GREEN}  ✓${NC} $line"
            fi
        done
    fi
    
    # Si solo queremos verificar conexión, salir aquí
    if [ "$CHECK_ONLY" = true ]; then
        log_success "Conexión con cámara verificada exitosamente"
        exit 0
    fi
}

# Obtener lista de configuraciones
get_config_list() {
    log_verbose "Obteniendo lista de configuraciones..."
    
    if ! gphoto2 --list-config > "$TEMP_LIST" 2>"$ERROR_LOG"; then
        log_error "No se pudo obtener lista de configuraciones"
        if [ -f "$ERROR_LOG" ]; then
            echo "Error gphoto2:"
            cat "$ERROR_LOG"
        fi
        exit 1
    fi
    
    local config_count=$(wc -l < "$TEMP_LIST")
    log_verbose "Encontradas $config_count entradas de configuración"
    
    if [ $config_count -eq 0 ]; then
        log_warning "No se encontraron configuraciones"
        exit 1
    fi
}

# Función para escapar JSON
escape_json() {
    echo "$1" | sed 's/\\/\\\\/g' | sed 's/"/\\"/g' | sed 's/$/\\n/' | tr -d '\n'
}

# Obtener configuración individual
get_single_config() {
    local config_name="$1"
    local output=""
    
    log_verbose "Obteniendo configuración: $config_name"
    
    # Intentar obtener configuración con timeout
    if output=$(timeout 10s gphoto2 --get-config "$config_name" 2>/dev/null); then
        echo "$output"
        return 0
    else
        log_warning "No se pudo obtener configuración para: $config_name"
        return 1
    fi
}

# Procesar todas las configuraciones
process_all_configs() {
    local total_configs=$(wc -l < "$TEMP_LIST")
    local current=0
    local success=0
    local failed=0
    
    log_verbose "Procesando $total_configs configuraciones..."
    
    # Crear archivo de salida
    if [ "$JSON_OUTPUT" = true ]; then
        echo "{" > "$OUTPUT_FILE"
        echo "  \"camera_config\": {" >> "$OUTPUT_FILE"
        echo "    \"generated_at\": \"$(date -Iseconds)\"," >> "$OUTPUT_FILE"
        echo "    \"generated_by\": \"gphoto_config_dump.sh\"," >> "$OUTPUT_FILE"
        echo "    \"camera_info\": \"$(gphoto2 --auto-detect 2>/dev/null | tail -n +3 | head -n 1)\"," >> "$OUTPUT_FILE"
        echo "    \"configurations\": {" >> "$OUTPUT_FILE"
    else
        cat > "$OUTPUT_FILE" << EOF
================================================================
CONFIGURACIÓN COMPLETA DE CÁMARA GPHOTO2
================================================================
Generado: $(date)
Script: gphoto_config_dump.sh
Cámara: $(gphoto2 --auto-detect 2>/dev/null | tail -n +3 | head -n 1)
================================================================

EOF
    fi
    
    # Procesar cada configuración
    while IFS= read -r config_name; do
        current=$((current + 1))
        
        if [ "$VERBOSE" = true ]; then
            printf "\r${CYAN}[%d/%d]${NC} Procesando: %-30s" "$current" "$total_configs" "$config_name"
        fi
        
        if config_data=$(get_single_config "$config_name"); then
            if [ "$JSON_OUTPUT" = true ]; then
                # Formato JSON
                local escaped_name=$(escape_json "$config_name")
                local escaped_data=$(escape_json "$config_data")
                
                if [ $success -gt 0 ]; then
                    echo "," >> "$OUTPUT_FILE"
                fi
                echo -n "      \"$escaped_name\": \"$escaped_data\"" >> "$OUTPUT_FILE"
            else
                # Formato texto
                echo "================================================================" >> "$OUTPUT_FILE"
                echo "CONFIGURACIÓN: $config_name" >> "$OUTPUT_FILE"
                echo "================================================================" >> "$OUTPUT_FILE"
                echo "$config_data" >> "$OUTPUT_FILE"
                echo "" >> "$OUTPUT_FILE"
            fi
            success=$((success + 1))
        else
            failed=$((failed + 1))
        fi
        
    done < "$TEMP_LIST"
    
    # Finalizar archivo
    if [ "$JSON_OUTPUT" = true ]; then
        echo "" >> "$OUTPUT_FILE"
        echo "    }," >> "$OUTPUT_FILE"
        echo "    \"summary\": {" >> "$OUTPUT_FILE"
        echo "      \"total_configs\": $total_configs," >> "$OUTPUT_FILE"
        echo "      \"successful\": $success," >> "$OUTPUT_FILE"
        echo "      \"failed\": $failed" >> "$OUTPUT_FILE"
        echo "    }" >> "$OUTPUT_FILE"
        echo "  }" >> "$OUTPUT_FILE"
        echo "}" >> "$OUTPUT_FILE"
    else
        echo "================================================================" >> "$OUTPUT_FILE"
        echo "RESUMEN" >> "$OUTPUT_FILE"
        echo "================================================================" >> "$OUTPUT_FILE"
        echo "Total configuraciones: $total_configs" >> "$OUTPUT_FILE"
        echo "Exitosas: $success" >> "$OUTPUT_FILE"
        echo "Fallidas: $failed" >> "$OUTPUT_FILE"
        echo "Archivo generado: $OUTPUT_FILE" >> "$OUTPUT_FILE"
        echo "================================================================" >> "$OUTPUT_FILE"
    fi
    
    if [ "$VERBOSE" = true ]; then
        echo # Nueva línea después del progreso
    fi
    
    log_success "Procesamiento completado:"
    echo -e "${GREEN}  ✓${NC} Configuraciones exitosas: $success"
    if [ $failed -gt 0 ]; then
        echo -e "${YELLOW}  ⚠${NC} Configuraciones fallidas: $failed"
    fi
    echo -e "${BLUE}  📄${NC} Archivo generado: $OUTPUT_FILE"
}

# Limpiar archivos temporales
cleanup() {
    rm -f "$TEMP_LIST" "$ERROR_LOG"
}

# Configurar trap para limpiar en caso de interrupción
trap cleanup EXIT INT TERM

# Función principal
main() {
    echo -e "${BLUE}=================================================================="
    echo -e "         Extractor de Configuración gPhoto2"
    echo -e "==================================================================${NC}"
    echo
    
    # Verificaciones iniciales
    check_gphoto2
    check_camera_connection
    
    # Obtener y procesar configuraciones
    get_config_list
    process_all_configs
    
    echo
    log_success "¡Proceso completado exitosamente!"
    
    # Mostrar información del archivo
    if [ -f "$OUTPUT_FILE" ]; then
        local file_size=$(du -h "$OUTPUT_FILE" | cut -f1)
        echo -e "${CYAN}Información del archivo:${NC}"
        echo -e "  📁 Archivo: $OUTPUT_FILE"
        echo -e "  📏 Tamaño: $file_size"
        echo -e "  🕒 Creado: $(date)"
        
        if [ "$JSON_OUTPUT" = true ]; then
            echo -e "  📋 Formato: JSON"
        else
            echo -e "  📋 Formato: Texto plano"
        fi
    fi
    
    echo
    echo -e "${GREEN}Para ver el archivo:${NC}"
    echo -e "  ${CYAN}less \"$OUTPUT_FILE\"${NC}     # Visualizar paginado"
    echo -e "  ${CYAN}cat \"$OUTPUT_FILE\"${NC}      # Mostrar completo"
    
    if [ "$JSON_OUTPUT" = true ]; then
        echo -e "  ${CYAN}jq . \"$OUTPUT_FILE\"${NC}    # Formatear JSON (si tienes jq instalado)"
    fi
}

# Ejecutar función principal
main "$@"

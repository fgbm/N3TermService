import requests


class N3TermService:
    def __init__(self, base_url: str, mis_guid: str):
        """Сервис терминологии

        :param base_url: Базовый URL для сервиса терминологии
        :param mis_guid: Идентификатор информационной системы
        """
        self.base_url = base_url
        self.mis_guid = mis_guid
        self.last_error = 0

    def _get_headers(self):
        return {'Authorization': f'N3 {self.mis_guid}', 'Content-Type': 'application/json'}

    def _post(self, entry_point: str, **parameters):
        """Метод POST для сервиса терминологии

        :param entry_point: Точка входа метода
        :param parameters: Параметры, передаваемые в теле запроса
        :return: Результат запроса в JSON, либо None
        """
        params = {
            'resourceType': 'Parameters',
            'parameter': [{'name': p, 'valueString': parameters[p]} for p in parameters if parameters[p] is not None]
        }
        r = requests.post(f'{self.base_url}{entry_point}', headers=self._get_headers(), json=params)
        self.last_error = r.status_code
        if r.status_code == 200:
            return r.json()
        else:
            return None

    def _get(self, entry_point, **parameters):
        """Метод GET для сервиса терминологии

        :param entry_point: Точка входа метода
        :param parameters: Параметры, передаваемые в строке запроса
        :return: Результат запроса в JSON, либо None
        """
        params = {'_format': 'json'}.update({p: parameters[p] for p in parameters})
        r = requests.get(f'{self.base_url}{entry_point}', headers=self._get_headers(), params=params)
        self.last_error = r.status_code
        if r.status_code == 200:
            return r.json()
        else:
            return None

    def info(self, oid: str):
        """Запрос справочника

        :param oid: Значение OID кодовой системы
        :return: Детальная информация о справочнике
        """
        return self._get('/ValueSet', url=f'urn:oid:{oid}')

    def expand(self, oid: str, version: int = None):
        """Запрос значений справочника

        :param oid: Значение OID кодовой системы
        :param version: Номер версии справочника. Если номер версии не указан, то возвращаются значения из актуальной версии
        :return: Метаинформация о справочнике и пары код-значение
        """
        return self._post('/ValueSet/$expand', system=f'urn:oid:{oid}', version=version)

    def lookup(self, oid: str, code: str, version: int = None):
        """Поиск значения в справочнике

        :param oid: Значение OID кодовой системы
        :param code: Код значения в справочнике
        :param version: Номер версии справочника. Если номер версии не указан, то возвращаются значения из актуальной версии
        :return: Массив дополнительных параметров значения справочника, соответствующего коду
        """
        return self._post('/ValueSet/$lookup', system=f'urn:oid:{oid}', code=code, version=version)

    def history(self, resource_guid: str):
        """Запрос списка версий справочника

        :param resource_guid: Идентификатор справочника в сервисе терминологии
        :return: Массив с информацией по каждой версии справочника
        """
        return self._get(f'/ValueSet/{resource_guid}/_history')

    def validate(self, oid: str, code: str, version: int = None):
        """Валидация значения в справочнике

        :param oid: Значение OID кодовой системы
        :param code: Код значения в справочнике
        :param version: Номер версии справочника. Если номер версии не указан, то возвращаются значения из актуальной версии
        :return: Результат проверки значения справочника
        """
        return self._post('/ValueSet/$validate-code', system=f'urn:oid:{oid}', code=code, version=version)

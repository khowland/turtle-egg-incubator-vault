from unittest.mock import MagicMock

def build_table_aware_mock(table_data_map):
    """
    Creates a mock Supabase client where .table(name) returns a mock
    that is pre-configured with the data in table_data_map[name].
    Supports recursive chainable calls while sharing the same data container.
    """
    mock_supabase = MagicMock()
    table_mocks = {}
    
    def get_table_mock(name):
        if name in table_mocks:
            return table_mocks[name]
        
        data = table_data_map.get(name, [])
        exec_mock = MagicMock()
        exec_mock.data = data
        exec_mock.count = len(data)

        # The core mock for this table
        tm = MagicMock()
        
        # All chainable methods return the SAME mock instance
        # so that .execute() always hits the same shared data.
        tm.select.return_value = tm
        tm.eq.return_value = tm
        tm.neq.return_value = tm
        tm.in_.return_value = tm
        tm.order.return_value = tm
        tm.limit.return_value = tm
        tm.upsert.return_value = tm
        tm.update.return_value = tm
        tm.insert.return_value = tm
        tm.execute.return_value = exec_mock
        
        table_mocks[name] = tm
        return tm
        
    mock_supabase.table.side_effect = get_table_mock
    return mock_supabase, table_mocks


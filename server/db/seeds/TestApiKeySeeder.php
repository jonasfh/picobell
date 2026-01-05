<?php
declare(strict_types=1);

use Phinx\Seed\AbstractSeed;

class TestApiKeySeeder extends AbstractSeed
{
    public function run(): void
    {
        // 1. Get the 'apartments' table
        $apartmentsTable = $this->table('apartments');
        $prefix = $this->getAdapter()->getOption('table_prefix');

        // 2. Check if we have any apartment
        $row = $this->fetchRow("SELECT * FROM {$prefix}apartments LIMIT 1");

        if ($row) {
            // 3. Update existing apartment with the test API key
            $sql = "UPDATE {$prefix}apartments SET api_key = '1234abcd', modified_at = :mod WHERE id = :id";
            $this->execute($sql, [
                'mod' => date('Y-m-d H:i:s'),
                'id' => $row['id']
            ]);
        } else {
            // 4. Create a new apartment if none exists
            $data = [
                'address'     => 'Testgate 1, Testby',
                'pico_serial' => 'TEST_PICO_001',
                'api_key'     => '1234abcd',
                'created_at'  => date('Y-m-d H:i:s'),
                'modified_at' => date('Y-m-d H:i:s'),
            ];
            $apartmentsTable->insert($data)->save();
        }
    }
}

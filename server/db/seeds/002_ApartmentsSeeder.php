<?php
declare(strict_types=1);

use Phinx\Seed\AbstractSeed;

final class ApartmentsSeeder extends AbstractSeed
{
    public function run(): void
    {
        $data = [
            [
                'address' => 'Storgata 1, Oslo',
                'pico_serial' => 'PICO123456',
                'created_at' => date('Y-m-d H:i:s'),
                'modified_at' => date('Y-m-d H:i:s'),
            ],
        ];

        $apartments = $this->table('apartments');
        $apartments->insert($data)->save();
    }
}
